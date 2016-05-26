from collections import OrderedDict

# (VER_MAJOR, VER_MINOR)
_MIN_RT_VER = (2, 3)
_MAX_RT_VER = (3, 15)

# Only schemas and default flags which are different from the
# immediately-preceeding version need to be provided.

# Format ('attribute_name', ('data_type', count))
# Must be OrderedDict - the order of items is vital.
_header_schemas = {
    '0203': OrderedDict([
        ('_endian_check', ('i4', 1)),
        ('ver_major', ('i4', 1)),
        ('ver_minor', ('i4', 1)),
        ('N_cells', ('i4', 1)),
        ('N_LOS', ('i4', 1)),
        ('_padding', ('i4', 251)),
    ]),

    # v3.6 identical header to v 2.3

    '0309': OrderedDict([
        ('_endian_check', ('i4', 1)),
        ('ver_major', ('i4', 1)),
        ('ver_minor', ('i4', 1)),
        ('N_cells', ('i4', 1)),
        ('N_LOS', ('i4', 1)),
        ('flag_rates', ('i4', 1)),
        ('flag_velocities', ('i4', 1)),
        ('flag_Ncols', ('i4', 1)),
        ('flag_refinements', ('i4', 1)),
        ('flag_single', ('i4', 1)),

        ('_padding1', ('i4', 118)),

        ('expansion_factor', ('f4', 1)),
        ('redshift', ('f4', 1)),
        ('time', ('f4', 1)),

        ('_padding2', ('f4', 125)),
    ]),

    # v3.11 identical header to v3.9
}

# Format ('attribute_name', boolean_value)
_default_flags = {
    '0203': {
        'flag_velocities': True,
        'flag_refinements': True,
        'flag_single': False,
        'flag_dR': False,
        'flag_n': True,
        'flag_tau': True,
        'flag_rates': True,
        'flag_Dold': False,
        'flag_Ncols': False,
    },

    '0306': {
        'flag_velocities': True,
        'flag_refinements': True,
        'flag_single': False,
        'flag_dR': False,
        'flag_n': True,
        'flag_tau': True,
        'flag_rates': False,
        'flag_Dold': True,
        'flag_Ncols': True,
    },

    '0309': {
        'flag_dR': True,
        'flag_n': False,
        'flag_tau': False,
        'flag_Dold': False,
    },
}

# Similar format to that used for headers. However, if the data type is simply
# 'f', it is determined from header.single; if the number of elements is a
# string, it is resolved to self.<string>, where string may contain '.'
# (i.e. self.header.N_cells will be correctly resolved).
# A third argument may be entered in the value-tuple specifying a dependency
# flag. This block will only be read if self.<flag> evaluates to true.
# Since flags are typically a part of the header, dependencies will likely be of
# the form 'header.flag_name'.

# Note that order is slightly different between version, hence all the
# almost-duplication.
_data_schemas = {
    '0203': OrderedDict([
        ('G', ('f8', 'header.N_cells')),
        ('n', ('f8', 'header.N_cells')),
        ('T', ('f8', 'header.N_cells')),
        ('L', ('f8', 'header.N_cells')),
        ('n_H', ('f8', 'header.N_cells')),
        ('x_H1', ('f8', 'header.N_cells')),
        ('x_H2', ('f8', 'header.N_cells')),
        ('n_He', ('f8', 'header.N_cells')),
        ('x_He1', ('f8', 'header.N_cells')),
        ('x_He2', ('f8', 'header.N_cells')),
        ('x_He3', ('f8', 'header.N_cells')),
        ('R', ('f8', 'header.N_cells')),
        ('D', ('f8', 'header.N_cells')),
        ('tau_H1', ('f8', 'header.N_cells')),
        ('G_H1', ('f8', 'header.N_cells')),
        ('G_He1', ('f8', 'header.N_cells')),
        ('G_He2', ('f8', 'header.N_cells')),
        ('gamma_H1', ('f8', 'header.N_cells')),
        ('gamma_He1', ('f8', 'header.N_cells')),
        ('gamma_He2', ('f8', 'header.N_cells')),
        ('L_H1', ('f8', 'header.N_cells')),
        ('L_He1', ('f8', 'header.N_cells')),
        ('L_He2', ('f8', 'header.N_cells')),
        ('L_eH', ('f8', 'header.N_cells')),
        ('L_C', ('f8', 'header.N_cells')),
        ('E_H1', ('f8', 'header.N_cells')),
        ('E_He1', ('f8', 'header.N_cells')),
        ('E_He2', ('f8', 'header.N_cells')),
        ('Ncol_H1', ('f8', 'header.N_cells')),
        ('Ncol_He1', ('f8', 'header.N_cells')),
        ('Ncol_He2', ('f8', 'header.N_cells')),
        ('v_z', ('f8', 'header.N_cells')),
        ('v_x', ('f8', 'header.N_cells')),
        ('entropy', ('f8', 'header.N_cells')),
        ('cell_buffer_index', ('i8', 'header.N_cells')),
        ('cell', ('i4', 1)),
        # Leading underscore  means read but not stored. Use header.N_cells.
        ('_N_cells', ('i4', 1)),
    ]),

    '0302': OrderedDict([
        ('N_cells', ('i4', 1)),
        ('cell', ('i4', 1)),
        ('N_bytes', ('i4', 1)),
        ('R', ('f', 'N_cells')),
        ('D', ('f', 'N_cells')),
        ('Dold', ('f', 'N_cells')),
        ('entropy', ('f', 'N_cells')),
        ('T', ('f', 'N_cells')),
        ('tau_H1', ('f', 'N_cells')),
        ('n', ('f', 'N_cells')),
        ('n_H', ('f', 'N_cells')),
        ('x_H1', ('f', 'N_cells')),
        ('x_H2', ('f', 'N_cells')),
        ('n_He', ('f', 'N_cells')),
        ('x_He1', ('f', 'N_cells')),
        ('x_He2', ('f', 'N_cells')),
        ('x_He3', ('f', 'N_cells')),
        ('G', ('f', 'N_cells')),
        ('G_H1', ('f', 'N_cells')),
        ('G_He1', ('f', 'N_cells')),
        ('G_He2', ('f', 'N_cells')),
        ('gamma_H1', ('f', 'N_cells')),
        ('gamma_He1', ('f', 'N_cells')),
        ('gamma_He2', ('f', 'N_cells')),
        ('L', ('f', 'N_cells')),
        ('L_H1', ('f', 'N_cells')),
        ('L_He1', ('f', 'N_cells')),
        ('L_He2', ('f', 'N_cells')),
        ('L_eH', ('f', 'N_cells')),
        ('L_C', ('f', 'N_cells')),
        ('E_H1', ('f', 'N_cells')),
        ('E_He1', ('f', 'N_cells')),
        ('E_He2', ('f', 'N_cells')),
        ('Ncol_H1', ('f', 'N_cells')),
        ('Ncol_He1', ('f', 'N_cells')),
        ('Ncol_He2', ('f', 'N_cells')),
        ('v_z', ('f', 'N_cells')),
        ('v_x', ('f', 'N_cells')),
        ('Ncols', ('f', 12)),
        ('cell_buffer_index', ('i8', 'N_cells')),
    ]),

    '0306': OrderedDict([
        ('N_cells', ('i4', 1)),
        ('cell', ('i4', 1)),
        ('N_bytes', ('i4', 1)),
        ('R', ('f', 'N_cells')),
        ('D', ('f', 'N_cells')),
        ('Dold', ('f', 'N_cells')),
        ('entropy', ('f', 'N_cells')),
        ('T', ('f', 'N_cells')),
        ('tau_H1', ('f', 'N_cells')),
        ('n', ('f', 'N_cells')),
        ('n_H', ('f', 'N_cells')),
        ('x_H1', ('f', 'N_cells')),
        ('x_H2', ('f', 'N_cells')),
        ('n_He', ('f', 'N_cells')),
        ('x_He1', ('f', 'N_cells')),
        ('x_He2', ('f', 'N_cells')),
        ('x_He3', ('f', 'N_cells')),
        ('Ncol_H1', ('f', 'N_cells')),
        ('Ncol_He1', ('f', 'N_cells')),
        ('Ncol_He2', ('f', 'N_cells')),
        ('v_z', ('f', 'N_cells')),
        ('v_x', ('f', 'N_cells')),
        ('Ncols', ('f', 12)),
        ('cell_buffer_index', ('i8', 'N_cells')),
    ]),

    '0309': OrderedDict([
        ('N_cells', ('u8', 1)),
        ('cell', ('u8', 1)),
        ('N_bytes', ('u8', 1)),
        ('R', ('f', 'N_cells')),
        ('dR', ('f', 'N_cells')),
        ('D', ('f', 'N_cells')),
        ('entropy', ('f', 'N_cells')),
        ('T', ('f', 'N_cells')),
        ('n_H', ('f', 'N_cells')),
        ('x_H1', ('f', 'N_cells')),
        ('x_H2', ('f', 'N_cells')),
        ('n_He', ('f', 'N_cells')),
        ('x_He1', ('f', 'N_cells')),
        ('x_He2', ('f', 'N_cells')),
        ('x_He3', ('f', 'N_cells')),
        ('Ncol_H1', ('f', 'N_cells')),
        ('Ncol_He1', ('f', 'N_cells')),
        ('Ncol_He2', ('f', 'N_cells')),

        ('G', ('f', 'N_cells', 'header.flag_rates')),
        ('G_H1', ('f', 'N_cells', 'header.flag_rates')),
        ('G_He1', ('f', 'N_cells', 'header.flag_rates')),
        ('G_He2', ('f', 'N_cells', 'header.flag_rates')),
        ('gamma_H1', ('f', 'N_cells', 'header.flag_rates')),
        ('gamma_He1', ('f', 'N_cells', 'header.flag_rates')),
        ('gamma_He2', ('f', 'N_cells', 'header.flag_rates')),
        ('L', ('f', 'N_cells', 'header.flag_rates')),
        ('L_H1', ('f', 'N_cells', 'header.flag_rates')),
        ('L_He1', ('f', 'N_cells', 'header.flag_rates')),
        ('L_He2', ('f', 'N_cells', 'header.flag_rates')),
        ('L_eH', ('f', 'N_cells', 'header.flag_rates')),
        ('L_C', ('f', 'N_cells', 'header.flag_rates')),
        ('E_H1', ('f', 'N_cells', 'header.flag_rates')),
        ('E_He1', ('f', 'N_cells', 'header.flag_rates')),
        ('E_He2', ('f', 'N_cells', 'header.flag_rates')),

        ('v_z', ('f', 'N_cells', 'header.flag_velocities')),
        ('v_x', ('f', 'N_cells', 'header.flag_velocities')),

        ('Ncols', ('f', 12, 'header.flag_Ncols')),

        ('cell_buffer_index', ('i8', 'N_cells', 'header.flag_refinements')),
    ]),
}
