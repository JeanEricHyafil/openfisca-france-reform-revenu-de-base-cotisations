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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import division

import copy

from openfisca_core import columns, formulas, reforms
from openfisca_france import entities, model
from openfisca_france.model.base import *


# Build function

def build_reform(tax_benefit_system):
    ReformeCotisationsRDB = reforms.make_reform(
        name = u"Réforme des cotisations pour un Revenu de base",
        reference = tax_benefit_system,
        )


    @ReformeCotisationsRDB.formula
    class cotisations_contributives(SimpleFormulaColumn):
        column = FloatCol
        entity_class = Individus
        label = u"Nouvelles cotisations contributives"

        def function(self, simulation, period):
            ags = simulation.calculate('ags', period)
            agff_tranche_a_employeur = simulation.calculate('agff_tranche_a_employeur', period)
            apec_employeur = simulation.calculate('apec_employeur', period)
            arrco_tranche_a_employeur = simulation.calculate('arrco_tranche_a_employeur', period)
            assedic_employeur = simulation.calculate('assedic_employeur', period)
            cotisation_exceptionnelle_temporaire_employeur = simulation.calculate('cotisation_exceptionnelle_temporaire_employeur', period)
            fonds_emploi_hospitalier = simulation.calculate('fonds_emploi_hospitalier', period)
            ircantec_employeur = simulation.calculate('ircantec_employeur', period)
            pension_civile_employeur = simulation.calculate('pension_civile_employeur', period)
            prevoyance_obligatoire_cadre = simulation.calculate('prevoyance_obligatoire_cadre', period)
            rafp_employeur = simulation.calculate('rafp_employeur', period)
            vieillesse_deplafonnee_employeur = simulation.calculate('vieillesse_deplafonnee_employeur', period)
            vieillesse_plafonnee_employeur = simulation.calculate('vieillesse_plafonnee_employeur', period)
            allocations_temporaires_invalidite = simulation.calculate('allocations_temporaires_invalidite', period)
            accident_du_travail = simulation.calculate('accident_du_travail', period)
            agff_tranche_a_employe = simulation.calculate('agff_tranche_a_employe', period)
            agirc_tranche_b_employe = simulation.calculate('agirc_tranche_b_employe', period)
            apec_employe = simulation.calculate('apec_employe', period)
            arrco_tranche_a_employe = simulation.calculate('arrco_tranche_a_employe', period)
            assedic_employe = simulation.calculate('assedic_employe', period)
            cotisation_exceptionnelle_temporaire_employe = simulation.calculate('cotisation_exceptionnelle_temporaire_employe', period)
            ircantec_employe = simulation.calculate('ircantec_employe', period)
            pension_civile_employe = simulation.calculate('pension_civile_employe', period)
            rafp_employe = simulation.calculate('rafp_employe', period)
            vieillesse_deplafonnee_employe = simulation.calculate('vieillesse_deplafonnee_employe', period)
            vieillesse_plafonnee_employe = simulation.calculate('vieillesse_plafonnee_employe', period)

            cotisations_contributives = (
                # cotisations patronales contributives dans le prive
                ags +
                agff_tranche_a_employeur +
                apec_employeur +
                arrco_tranche_a_employeur +
                assedic_employeur +
                cotisation_exceptionnelle_temporaire_employeur +
                prevoyance_obligatoire_cadre +  # TODO contributive ou pas
                vieillesse_deplafonnee_employeur +
                vieillesse_plafonnee_employeur +
                # cotisations patronales contributives dans le public
                fonds_emploi_hospitalier +
                ircantec_employeur +
                pension_civile_employeur +
                rafp_employeur +
                # anciennes cot patronales non-contributives classées ici comme contributives
                allocations_temporaires_invalidite +
                accident_du_travail +
                # anciennes cotisations salariales contributives dans le prive
                agff_tranche_a_employe +
                agirc_tranche_b_employe +
                apec_employe +
                arrco_tranche_a_employe +
                assedic_employe +
                cotisation_exceptionnelle_temporaire_employe +
                vieillesse_deplafonnee_employe +
                vieillesse_plafonnee_employe +
                # anciennes cotisations salariales contributives dans le public
                ircantec_employe +
                pension_civile_employe +
                rafp_employe
                )
            return period, cotisations_contributives


    @ReformeCotisationsRDB.formula
    class nouv_salbrut(SimpleFormulaColumn):
        reference = tax_benefit_system.column_by_name['salbrut']

        # Le salaire brut se définit dans la réforme comme le salaire super-brut auquel
        # on retranche les cotisations contributives

        def function(self, simulation, period):
            period = period.start.period('month').offset('first-of')
            salsuperbrut = simulation.calculate('salsuperbrut', period)
            cotisations_contributives = simulation.calculate('cotisations_contributives', period)

            nouv_salbrut = (
                salsuperbrut -
                cotisations_contributives
                )
            return period, nouv_salbrut


    @ReformeCotisationsRDB.formula
    class nouv_csg(SimpleFormulaColumn):
        reference = tax_benefit_system.column_by_name['csgsali']

        # On applique une CSG unique à 22,5% qui finance toutes les prestations non-contributives

        def function(self, simulation, period):
            period = period.start.period('month').offset('first-of')
            nouv_salbrut = simulation.calculate('nouv_salbrut', period)

            nouv_csg = (
                -0.225 * nouv_salbrut
                )
            return period, nouv_csg


    @ReformeCotisationsRDB.formula
    class salnet(SimpleFormulaColumn):
        reference = tax_benefit_system.column_by_name['salnet']

        # On retire la nouvelle CSG (pas celle qui finance le RDB) pour trouver le nouveau salaire net

        def function(self, simulation, period):
            period = period.start.period('month').offset('first-of')
            nouv_salbrut = simulation.calculate('nouv_salbrut', period)
            nouv_csg = simulation.calculate('nouv_csg', period)

            salnet = (
                nouv_salbrut +
                nouv_csg
                )
            return period, salnet


    @ReformeCotisationsRDB.formula
    class sal(SimpleFormulaColumn):
        reference = tax_benefit_system.column_by_name['sal']

        # Nous sommes partis du nouveau salaire net et par rapport au salaire imposable actuel,
        # nous avons supprimé : les heures sup, la déductibilité de CSG


        def function(self, simulation, period):
            period = period
            hsup = simulation.calculate('hsup', period)
            salnet = simulation.calculate('salnet', period)
            primes_fonction_publique = simulation.calculate('primes_fonction_publique', period)
            indemnite_residence = simulation.calculate('indemnite_residence', period)
            supp_familial_traitement = simulation.calculate('supp_familial_traitement', period)
            rev_microsocial_declarant1 = simulation.calculate('rev_microsocial_declarant1', period)

            return period, (
                salnet +
                primes_fonction_publique +
                indemnite_residence +
                supp_familial_traitement +
                hsup +
                rev_microsocial_declarant1
                )


    return ReformeCotisationsRDB()
