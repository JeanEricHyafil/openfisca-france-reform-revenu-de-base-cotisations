# -*- coding: utf-8 -*-


# OpenFisca -- A versatile microsimulation software
# By: OpenFisca Team <contact@openfisca.fr>
#
# Copyright (C) 2011, 2012, 2013, 2014 OpenFisca Team
# https://github.com/openfisca
#
# This file is part of OpenFisca.
#
# OpenFisca is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenFisca is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE,  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program,  If not, see <http://www.gnu.org/licenses/>.


from datetime import date

from openfisca_france.tests.base import tax_benefit_system
from openfisca_core.tools import assert_near

import openfisca_france_reform_revenu_de_base_cotisations


def test():
    reform = openfisca_france_reform_revenu_de_base_cotisations.build_reform(tax_benefit_system)
    reform_simulation = reform.new_scenario().init_single_entity(
        period = 2014,
        parent1 = dict(
            birth = date(1980, 1, 1),
            sali = 12000,
            ),
        parent2 = dict(
            birth = date(1980, 1, 1),
            sali = 6000,
            ),
        enfants = [
            dict(
                birth = date(2014, 1, 1),
                ),
            ],
        ).new_simulation(debug = True)

    error_margin = 0.01

    assert_near(
        reform_simulation.calculate('salsuperbrut'),
        [17051.3046875, 8525.65234375, 0],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('cotisations_contributives'),
        [-5141.63378906, -2570.81689453, 0],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('nouv_salbrut'),
        [22192.93945312, 11096.46972656, 0],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('salbrut'),
        [14825.93261719, 7412.96630859, 0],
        error_margin = error_margin,
        )
    assert_near(
        reform_simulation.calculate('salnet'),
        [17199.52734375, 8599.76367188, 0],
        error_margin = error_margin,
        )
