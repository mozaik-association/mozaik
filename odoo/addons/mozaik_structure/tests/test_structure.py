# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo import exceptions


class TestStructure(TransactionCase):

    def _get_a_partner(self, is_company):
        return self.env['res.partner'].create({
            'name': 'Melania Trump',
            'is_company': is_company,
        })

    def test_power_level_consistency(self):
        '''
        Cannot create an assembly with a category and an instance of
        different power level
        '''

        # internal assembly data with inconsistence power level
        data = {
            'name': 'wrong assembly',
            'assembly_category_id':
            self.ref('mozaik_structure.int_assembly_category_01'),
            'instance_id':
            self.ref('mozaik_structure.int_instance_02'),
        }

        # create the assembly: NOK
        self.assertRaises(
            exceptions.ValidationError,
            self.env['int.assembly'].create, data)

        # another power level
        data = {
            'power_level_id': self.ref('mozaik_structure.int_power_level_01'),
        }

        # change power level of an instance: NOK
        self.assertRaises(
            exceptions.ValidationError,
            self.browse_ref('mozaik_structure.int_instance_02').write, data)

        # another power level
        data = {
            'power_level_id': self.ref('mozaik_structure.int_power_level_02'),
        }

        # change power level of a category: NOK
        self.assertRaises(
            exceptions.ValidationError,
            self.browse_ref('mozaik_structure.int_assembly_category_01').write,
            data)

        # state assembly data with inconsistence power level
        data = {
            'name': 'wrong assembly',
            'assembly_category_id':
            self.ref('mozaik_structure.sta_assembly_category_01'),
            'instance_id':
            self.ref('mozaik_structure.sta_instance_02'),
        }

        # create the assembly: NOK
        self.assertRaises(
            exceptions.ValidationError,
            self.env['sta.assembly'].create, data)

        # another power level
        data = {
            'power_level_id': self.ref('mozaik_structure.sta_power_level_02'),
        }

        # change power level of an instance: NOK
        self.assertRaises(
            exceptions.ValidationError,
            self.browse_ref('mozaik_structure.sta_instance_01').write, data)

        # another power level
        data = {
            'power_level_id': self.ref('mozaik_structure.sta_power_level_01'),
        }

        # change power level of a category: NOK
        self.assertRaises(
            exceptions.ValidationError,
            self.browse_ref('mozaik_structure.sta_assembly_category_02').write,
            data)

        # get an external category
        ext_cat = self.browse_ref('mozaik_structure.ext_assembly_category_01')
        for i in range(1, 3):
            # change its (internal and unused) power level
            ext_cat.power_level_id = \
                self.ref('mozaik_structure.int_power_level_0%s' % i)

        return

    def test_company_and_assembly_flag(self):
        '''
        Assembly and company flag must be set after creating an assembly
        '''

        # get demo assemblies
        assemblies = [
            self.browse_ref('mozaik_structure.int_assembly_01'),
            self.browse_ref('mozaik_structure.sta_assembly_01'),
            self.browse_ref('mozaik_structure.ext_assembly_01'),
        ]

        # check flags
        self.assertTrue(all([a.partner_id.is_company for a in assemblies]))
        self.assertTrue(all([a.partner_id.is_assembly for a in assemblies]))

        # create a natural partner...
        p = self._get_a_partner(False)
        # ... and an external assembly arround it
        data = {
            'name': p.name,
            'assembly_category_id':
            self.ref('mozaik_structure.ext_assembly_category_01'),
            'ref_partner_id': p.id,
        }

        # create the assembly: NOK
        self.assertRaises(
            exceptions.ValidationError,
            self.env['ext.assembly'].create, data)

        # external assembly data arround a state assembly
        data = {
            'name': 'wrong assembly',
            'assembly_category_id':
            self.ref('mozaik_structure.ext_assembly_category_01'),
            'ref_partner_id':
            self.browse_ref('mozaik_structure.sta_assembly_01').partner_id.id,
        }

        # create the assembly: NOK
        self.assertRaises(
            exceptions.ValidationError,
            self.env['ext.assembly'].create, data)

        return

    def test_get_secretariat(self):
        '''
        Check for secretariat associated to an internal instance or assembly
        '''
        assembly1 = self.browse_ref('mozaik_structure.int_assembly_01')
        assembly2 = self.browse_ref('mozaik_structure.int_assembly_02')

        # check for demo data
        self.assertFalse(assembly1.is_secretariat)
        self.assertTrue(assembly2.is_secretariat)

        # retrieve and check secretariat of assemblies
        self.assertFalse(assembly1._get_secretariat())
        self.assertEqual(assembly2, assembly2._get_secretariat())

        # retrieve and check secretariat of assembly instances
        self.assertFalse(assembly1.instance_id._get_secretariat())
        self.assertEqual(assembly2, assembly2.instance_id._get_secretariat())

        return

    def test_get_followers(self):
        '''
        Check for followers associated to an internal instance reagrding
        the level_for_followers flag of the power level of all its ancestors
        '''
        instance = self.browse_ref('mozaik_structure.int_instance_02')
        assembly = self.browse_ref('mozaik_structure.int_assembly_02')

        # check for demo data
        self.assertEqual(
            assembly.partner_id, instance._get_instance_followers())

        # mega update on power levels and assembly categories
        self.env['int.power.level'].search([]).write(
            {'level_for_followers': True})
        self.env['int.assembly.category'].search([]).write(
            {'is_secretariat': True})

        # get all internal assembly partners
        partners = self.env['int.assembly'].search([]).mapped('partner_id')

        # check for followers
        self.assertEqual(
            partners, instance._get_instance_followers())

        return

    def test_instance_recursion(self):
        '''
        Check for recursion in the instance hirerachies
        '''
        instance2 = self.browse_ref('mozaik_structure.int_instance_02')

        # try a recursion: NOK
        self.assertRaises(
            exceptions.ValidationError,
            self.browse_ref('mozaik_structure.int_instance_01').write,
            {'parent_id': instance2.id})

        instance1 = self.browse_ref('mozaik_structure.sta_instance_01')
        instance2 = self.browse_ref('mozaik_structure.sta_instance_02')

        # try a recursion: NOK
        self.assertRaises(
            exceptions.ValidationError,
            instance1.write, {'parent_id': instance2.id})

        instance2.secondary_parent_id = instance1

        # try another recursion: NOK
        self.assertRaises(
            exceptions.ValidationError,
            instance1.write, {'secondary_parent_id': instance2.id})

        return

    def test_onchange_assembly_id(self):
        '''
        Check for _onchange_assembly_id on electoral district
        '''

        # electoral district data
        data = {
            'sta_instance_id':
            self.ref('mozaik_structure.sta_instance_01'),
            'assembly_id':
            self.ref('mozaik_structure.sta_assembly_02'),
        }

        # get a memory record and launch the onchange
        ed = self.env['electoral.district'].new(data)
        ed._onchange_assembly_id()

        # check for designation assembly
        self.assertEqual(
            self.browse_ref('mozaik_structure.int_assembly_02'),
            ed.designation_int_assembly_id)

    def test_onchange_assembly_category_or_instance(self):
        '''
        Check for _onchange_assembly_category_or_instance on internal assembly
        '''

        # get a memory record and launch the onchange
        ia = self.env['int.assembly'].new()
        ia._onchange_assembly_category_or_instance()

        # check for assembly name
        self.assertFalse(ia.name)

        # update record and launch the onchange
        ia.instance_id = self.ref('mozaik_structure.int_instance_01')
        ia._onchange_assembly_category_or_instance()

        # check for assembly name
        self.assertFalse(ia.name)

        # update record and launch the onchange
        ia.assembly_category_id = self.ref(
            'mozaik_structure.int_assembly_category_01')
        ia._onchange_assembly_category_or_instance()

        # check for assembly name
        self.assertTrue(ia.name)

        return

    def test_assembly_name(self):
        '''
        Check for assembly name if not given
        '''
        # get a state category and instance
        instance = self.browse_ref('mozaik_structure.sta_instance_01')
        cat = self.env['sta.assembly.category'].create({
            'name': 'Conseil de guerre',
            'power_level_id': self.ref('mozaik_structure.sta_power_level_01'),
        })

        # state assembly data
        data = {
            'assembly_category_id': cat.id,
            'instance_id': instance.id,
        }
        # create the assembly
        assembly = self.env['sta.assembly'].create(data)
        # check for its name
        self.assertEqual(
            '%s (%s)' % (instance.name, cat.name), assembly.name)

        # get an internal category and instance
        instance = self.browse_ref('mozaik_structure.int_instance_01')
        cat = self.env['int.assembly.category'].create({
            'name': 'Conseil de paix',
            'power_level_id': self.ref('mozaik_structure.int_power_level_01'),
        })

        # state assembly data
        data = {
            'assembly_category_id': cat.id,
            'instance_id': instance.id,
        }
        # create the assembly
        assembly = self.env['int.assembly'].create(data)
        # check for its name
        self.assertEqual(
            '%s (%s)' % (instance.name, cat.name), assembly.name)

        # create a natural partner
        p = self._get_a_partner(True)
        # get an external category
        cat = self.browse_ref('mozaik_structure.ext_assembly_category_01')

        # external assembly data
        data = {
            'assembly_category_id': cat.id,
            'ref_partner_id': p.id,
        }
        # create the assembly
        assembly = self.env['ext.assembly'].create(data)
        # check for its name
        self.assertEqual(
            '%s (%s)' % (p.name, cat.name), assembly.name)
