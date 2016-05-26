import sys
if sys.version_info >= (3, 0):
    from functools import reduce

import numpy as np

from .schemadict import schema_dict

def _rgetattr(x, name):
    return reduce(getattr, [x] + name.split('.'))

class RTHeader(object):
    """
    An RT header.

    Contains the attributes
        fname     Name of the current file
        version   A string of the form 'x.y' for the current file version
        ver_major Major version of RT data file
        ver_minor Minor version of RT data file
        N_cells   The length of each line of sight vector (unreliable)
        N_LOS     The number of line of sight vectors

    Notes that version is not known until a header has been loaded

    Note also that N_cells is unreliable, as in many versions of the RT data
    file format, each line of sight may contain a different number of cells.
    Use LOS.N_cells instead, where LOS is an RTLOS.

    The following boolean-like flags are also available. They are read from
    file for RT file format versions > 3.6, and set appropriately for all prior
    versions
        flag_rates       Set if rates are present
        flag_velocities  Set if velocities are present
        flag_Ncols       Set if ???
        flag_refinements Set if cell refinements are present (for AMR)
        flag_single      Set if data is single precision (otherwise double)

    Finally, the following boolean-like flags are available, but these are not
    present in any RT data file; they are set based purely on the RT data file
    version,
        flag_Dold Set if Dold is present
        flag_dR   Set if dR is present
        flag_n    Set if n (n_H + n_He) is present
        flag_tau  Set if tau_H1 is present
    """

    def __init__(self, fname=None):
        super(RTHeader, self).__init__()
        self._fname = fname
        self._byteorder = None
        self._version = None
        self._version_key = None

    @property
    def fname(self):
        return self._fname

    @fname.setter
    def fname(self, fname):
        # if fname != self._fname:
        #     self._byteorder = None
        #     self._version = None
        self._fname = fname

    @property
    def version(self):
        return "%d.%d" % self._version

    def load(self):
        """Load the header from the current file."""
        with open(self.fname, 'rb') as f:
            self._load_metadata(f)
            self._load(f)

    def _dtype(self, dtype):
        dtype_str = np.dtype(dtype).str[1:] # Strip off byte order character.
        return np.dtype(self._byteorder + dtype_str)

    def _get_byteorder(self, f):
        at = f.tell()
        f.seek(0)
        self._byteorder = '='
        check, = np.fromfile(f, self._dtype('i4'), 1)
        if check != 1:
            self._byteorder = '>' if sys.byteorder == 'little' else '<'
            f.seek(0)
            check, = np.fromfile(f, self._dtype('i4'), 1)
            if check != 1:
                raise RTDataIOError("Cannot determine endianness")
        f.seek(at)

    def _get_version(self, f):
        at = f.tell()
        f.seek(0)
        _, major, minor = np.fromfile(f, self._dtype('i4'), 3)
        self._version = (major, minor)
        self._version_key = "%02d%02d" % self._version
        f.seek(at)

    def _load_metadata(self, f):
        self._get_byteorder(f)
        self._get_version(f)
        f.seek(0)

    def _load(self, f):
        schema, flags, _ = schema_dict[self._version_key]
        for (name, fmt) in schema.items():
            dtype, count = fmt
            data = np.fromfile(f, self._dtype(dtype), count)
            if count == 1:
                data = data[0]
            if not name.startswith('_'):
                setattr(self, name, data)

        for (name, value) in flags.items():
            setattr(self, name, value)

class RTCell(object):
    """An RT cell.

    Contains the members
        R       The size of the cell                               [m]
        dR      The width of the cell                              [m]
        D       The density of the cell                            [kg/m^3]
        entropy The entropy of the cell                            [J/K]
        T       The temperature of the cell                        [K]
        n_H     The hydrogen number density of the cell            [m^-3]
        n_He    The helium number density of the cell              [m^-3]
        x_H1    The HI fraction of the cell                        [0, 1]
        x_H2    The HII fraction of the cell                       [0, 1]
        x_He1   The HeI fraction of the cell                       [0, 1]
        x_He2   The HeII fraction of the cell                      [0, 1]
        x_He3   The HeIII fraction of the cell                     [0, 1]

    Values which are not defined for the file version have a value of zero.
    """

    def __init__(self, R=0, D=0, entropy=0, T=0, n_H=0, n_He=0,
                 x_H1=0, x_H2=0, x_He1=0, x_He2=0, x_He3=0, dR=0):
        super(RTCell, self).__init__()
        self.R = R
        self.dR = dR
        self.D = D
        self.entropy = entropy
        self.T = T
        self.n_H = n_H
        self.n_He = n_He
        self.x_H1 = x_H1
        self.x_H2 = x_H2
        self.x_He1 = x_He1
        self.x_He2 = x_He2
        self.x_He3 = x_He3

    @classmethod
    def from_LOS(cls, LOS, i):
        cell = cls(LOS.R[i], LOS.D[i], LOS.entropy[i], LOS.T[i], LOS.n_H[i],
                   LOS.n_He[i], LOS.x_H1[i], LOS.x_H2[i], LOS.x_He1[i],
                   LOS.x_He2[i], LOS.x_H3[i])
        if LOS.header.flag_dR:
            cell.dR = LOS.dR[i]
        return cell

class RTLOS(object):
    """A single RT line of sight. Attributes depend on the RT file version."""
    def __init__(self, header):
        super(RTLOS, self).__init__()
        self.header = header

    @property
    def fname(self):
        return self.header.fname

    @property
    def _schema(self):
        _, _, schema = schema_dict[self.header._version_key]
        return schema

    def _load(self, f):
        for (name, fmt) in self._schema.items():
            if len(fmt) == 2:
                dtype, count = fmt
                flag = True
            else:
                dtype, count, flag = fmt

            if dtype == 'f':
                if self.header.flag_single:
                    dtype = 'f4'
                else:
                    dtype = 'f8'
            dtype = self.header._dtype(dtype)
            if isinstance(count, str):
                count = _rgetattr(self, count)
            if isinstance(flag, str):
                flag = _rgetattr(self, flag)

            if flag:
                data = np.fromfile(f, dtype, count)
                if count == 1:
                    data = data[0]
                if not name.startswith('_'):
                    setattr(self, name, data)

    def __getitem__(self, index):
        """Get the ith cell from the line of sight.

        Return a copy of the data as an RTCell.
        """
        if index >= self.N_cells or index < 0:
            raise IndexError("Cell index " + str(index) + " is out of bounds")

        return RTCell.from_LOS(self, index)

    def __setitem__(self, index, value):
        """Set the ith values for each of the line of sight properties.

        value should be an RTCell, or compatible object."""
        if index >= self.N_cells or index < 0:
            raise IndexError("Cell index " + str(index) + " is out of bounds")

        self.R[index] = value.R
        if self.header.flags.dR:
            self.dR[index] = value.dR
        self.D[index] = value.D
        self.entropy[index] = value.entropy
        self.T[index] = value.T
        self.n_H[index] = value.n_H
        self.n_He[index] = value.n_he
        self.x_H1[index] = value.x_H1
        self.x_H2[index] = value.x_H2
        self.x_He1[index] = value.x_He1
        self.x_He2[index] = value.x_He2
        self.x_He3[index] = value.x_He3

class RTData(object):
    """
    RT data along all lines of sight in an RT snapshot.

    Contains the members
        header The RT header (RTHeader) instance associated with this data
        LOS    A list of the N_LOS lines of sight (RTLOS) instances

    Lines of sight within LOS may be accessed as:
        d = RTData(filename)
        LOS_10 = d[10]
        LOS_10 is d.LOS[10] # True

    Contains the methods
        load Load all lines of sight from file
    """

    def __init__(self, fname):
        super(RTData, self).__init__()
        self._fname = fname
        self.header = RTHeader(fname)
        self.LOS = []

    @property
    def fname(self):
        return self.header.fname

    @fname.setter
    def fname(self, fname):
        self._fname = fname
        self.header.fname = fname

    def load(self):
        with open(self.fname, 'rb') as f:
            self.header._load_metadata(f)
            self.header._load(f)
            self.LOS = []
            for i in range(self.header.N_LOS):
                LOS = RTLOS(self.header)
                LOS._load(f)
                self.LOS.append(LOS)

    def __getitem__(self, index):
        """Get the ith line of sight.

        Modifying the returned LOS will modify the LOS in RTData.
        """
        return self.LOS[index]
