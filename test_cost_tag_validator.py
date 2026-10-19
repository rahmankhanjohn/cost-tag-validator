import tempfile
import unittest
from pathlib import Path

import cost_tag_validator as ctv

TF = '''
resource "aws_instance" "web" {
  tags = {
    tenant_id   = "cust_88213"
    environment = "prod"
    service     = "checkout-api"
    cost_center = "eng-42"
    owner       = "team-payments"
    tenancy     = "dedicated"
  }
}
'''

TF_MISSING = '''
resource "aws_instance" "web" {
  tags = {
    tenant_id = "cust_88213"
  }
}
'''

YAML = '''
metadata:
  labels:
    tenant_id: cust_88213
    environment: prod
    service: checkout-api
    cost_center: eng-42
    owner: Team-Payments
    tenancy: shared
'''

JSON_TAGS = '{"tags": {"tenant_id": "cust_1", "environment": "prod", "service": "svc", ' \
            '"cost_center": "eng-1", "owner": "team-x", "tenancy": "shared"}}'


class TestExtraction(unittest.TestCase):
    def test_terraform_tags(self):
        blocks = ctv.extract_tag_blocks(TF)
        self.assertTrue(blocks)
        self.assertEqual(blocks[0]['tenant_id'], 'cust_88213')
        self.assertEqual(blocks[0]['tenancy'], 'dedicated')

    def test_yaml_labels(self):
        blocks = ctv.extract_tag_blocks(YAML)
        self.assertTrue(blocks)
        self.assertEqual(blocks[0]['environment'], 'prod')
        self.assertEqual(blocks[0]['owner'], 'Team-Payments')

    def test_json_tags(self):
        blocks = ctv.extract_tag_blocks(JSON_TAGS)
        self.assertTrue(blocks)
        self.assertEqual(blocks[0]['service'], 'svc')

    def test_no_blocks_in_plain_file(self):
        self.assertEqual(ctv.extract_tag_blocks('hello world\n'), [])


class TestValidation(unittest.TestCase):
    def test_complete_block_passes(self):
        present, problems = ctv.validate_block(ctv.extract_tag_blocks(TF)[0])
        self.assertEqual(problems, [])
        self.assertIn('owner', present)

    def test_missing_keys_are_reported(self):
        _present, problems = ctv.validate_block(ctv.extract_tag_blocks(TF_MISSING)[0])
        kinds = {p[0] for p in problems}
        self.assertIn('missing_key', kinds)
        missing = {p[1] for p in problems}
        self.assertIn('environment', missing)
        self.assertIn('tenancy', missing)

    def test_bad_tenancy_value(self):
        block = dict(ctv.extract_tag_blocks(TF)[0])
        block['tenancy'] = 'hybrid'
        _present, problems = ctv.validate_block(block)
        self.assertIn('bad_tenancy', {p[0] for p in problems})

    def test_unknown_environment(self):
        block = dict(ctv.extract_tag_blocks(TF)[0])
        block['environment'] = 'production'
        _present, problems = ctv.validate_block(block)
        self.assertIn('unknown_environment', {p[0] for p in problems})

    def test_empty_value(self):
        block = dict(ctv.extract_tag_blocks(TF)[0])
        block['owner'] = ''
        _present, problems = ctv.validate_block(block)
        self.assertIn('empty_value', {p[0] for p in problems})


if __name__ == '__main__':
    unittest.main()
