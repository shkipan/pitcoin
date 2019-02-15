from wallet import *
from block import Block
from blockchain import Blockchain
from merkle import merkle_root
from script import Script

import unittest

class TestKeys(unittest.TestCase):
	priv_key = 'A0FB5053799715E8A32B5A8CA85681F82875C2717B41CFEA3A3FB9DA42BEB4C3'.lower()
	pub_key_compressed = '02F32BE0EF53AB8FBA520069AE3879D7171F52BFACB0E2BC4DBF67E5E6346F8CBC'.lower()
	pub_key_uncompressed = '04f32be0ef53ab8fba520069ae3879d7171f52bfacb0e2bc4dbf67e5e6346f8cbcfbda1ae085819ded36b1b083b6b12317f02bf3e9f9c1d1853ff99d9aa44a2ec6'
	address_compressed = '1MYcBYVZ1Ktck7chSe7NURhH3wmsSzyayC'.lower()
	bl = Block(1550106562.2110739, 0,  '0', [str(i) for i in range(9)])
	blc1 = Blockchain()


	def test_private_key_length(self):
		self.assertEqual(
			len(get_new_private_key()), 
			64, 
			'invalid length of private key') 

	def test_checksum(self):
		i = '0100000001d89f122c065a8a6835a324978045045e5e5d3f4a95043d3bb69e1a46e12bc101000000006a47304402202a6cb7578c283aac7f766de7fe56b2c1ed96491a9d20ed47167246fecb0cf36402201d70b6d4814ff3e3b0d34ef431bf67f729c401a4a7a221d0f7e05ce7ceaa7c260121030bd6af4572a569e8c512f686cd5b9f414a58b71cf1a54543b20afdbe9129b969ffffffff0100350c00000000001976a9149ee1c9c57e86f8d1264a02f8af8a5c2543f787bc88ac00000000'
		self.assertEqual(
				checksum(i),			
				hashlib.sha256(hashlib.sha256(bytes.fromhex(i)).digest()).hexdigest()[0:8],
				'Invalid checksum')

	def test_wif_convertion(self):
		pk = '2E5280151030CDA28DD0D651E0FCF6DD07B592D6A8C664BBFD0D3E817C86E02E'
		self.assertEqual(
			convert_to_wif(pk), 
			'cP8kE3fdKExwqETgSJp6wzhLHY54o86AodgMK1bCR5DDUTSjheFU',
			'Invalid wif format of private key')		

	def test_convert_from_wif(self):
		wif = 'cTuNpHRW4MxpchinjhPNaf87fRhXp4F5TeAZ38tKDuiDZforKYzp'	
		self.assertEqual(
			convert_from_wif(wif), 
			'bca1b49349e8f1b96dcb449925c8f92a4b99883fc85a8eb6f06d394e15a82aee',
			'Invalid conversion from wif format')	

	def test_pub_key_compressed(self):
		self.assertEqual(
			get_public_key(self.priv_key),
			self.pub_key_compressed,
			'Invalid compressed public key generated')

	def test_pub_key_uncompressed(self):
		self.assertEqual(
			get_public_key(self.priv_key, False), 
			self.pub_key_uncompressed,
			'Invalid uncompressed public key generated')

	def test_block_calculate_hash(self):
		self.assertEqual(
			self.bl.calculate_hash(), 
			'79f05ba52aeedaa5c1e5d70cce145007ce390be8946942a816bd1ed1267efb0c',
			'Invalid block hash calculated')

	def test_blockchain_mine(self):
		self.blc1.mine(self.bl)
		self.assertEqual(
			self.bl.calculate_hash()[:self.blc1.complexity],
			'0' * self.blc1.complexity,
			'Invalid number of zero bytes in block\'s hash after mining')

	def test_blockchain_empty(self):
		self.assertTrue(
			len(self.blc1.blocks) == 1,
			'Blockchain on init contains more than one block')

	def test_merkle_root(self):
		s = [str(i) for i in range(9)]
		self.assertEqual(
			'cc64e53910aa6b6234017147332041f889d647e841222b0a252853c4e72cd21a',
			merkle_root(s),
			'Invalid merkle root')

	def test_script_validation(self):
		scriptsig = '41289a5d2e0a373d2bc37713043f806290f28ecc7f5bb334011183fdec8e87bc7279b341f57e4a54bf76a89ec70873f7c6eaec6a7d02de8ccc6022872e6d96aa7f0141040bd6af4572a569e8c512f686cd5b9f414a58b71cf1a54543b20afdbe9129b9693b6b37493a4c5b8d716d2d93e5d34f9bd39753db8ecd59d9ec89b23dbf5ffdb1'
		script = '76a91432ecbb1b78a870466ed165d98165fba6ddb3828488ac'
		scr = Script('1f0b671930cf4d72983f8974c0ec6893a96c4202283e6d5b6271cec7d5497982')
		self.assertTrue(
    		scr.decode(script, scriptsig),
    		'Script wasn\'t validated')
	

if __name__ == '__main__':

	unittest.main()
	