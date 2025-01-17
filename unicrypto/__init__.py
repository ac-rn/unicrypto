import importlib
import importlib.util


#https://stackoverflow.com/questions/8790003/dynamically-import-a-method-in-a-file-from-a-string
def import_from(module, name):
	module = __import__(module, fromlist=[name])
	return getattr(module, name)

pref_to_module = {
	'mbedtls' : 'mbedtls',
	'cryptography' : 'cryptography',
	'pyCryptodome': 'Crypto',
	'pyCrypto' : 'pyCrypto', # remove the 'py' but you really shouldn't be using this...
	'pure': 'pure',

}

# preferred modules for each cipher, in order of preferance
preftable = {
	'DES' : ['pyCryptodome','cryptography','pyCrypto','mbedtls','pure'], 
	'TDES': ['pyCryptodome','cryptography','pyCrypto','mbedtls','pure'], 
	'AES' : ['pyCryptodome','cryptography','pyCrypto','mbedtls','pure'], 
	'RC4' : ['pyCryptodome','cryptography','pyCrypto','mbedtls','pure'],
}

available_modules = {
	'DES' : ['pure'],
	'TDES' : ['pure'],
	'AES' : ['pure'],
	'RC4' : ['pure'],
}

override_library = None

for prefname in pref_to_module:
	if importlib.util.find_spec(pref_to_module[prefname]) is not None:
		for k in available_modules:
			available_modules[k].append(prefname)

def get_cipher_by_name(ciphername, cryptolibname):
	moduleName = 'unicrypto.backends.%s.%s' % (cryptolibname.lower(), ciphername)
	return import_from(moduleName , ciphername)


def get_preferred_cipher(ciphername):
	if override_library is None:
		if ciphername not in preftable:
			raise Exception('Cipher "%s" is not supported!' % ciphername)
		#print('available_modules %s' % available_modules)
		possible_prefmodule = list(set(preftable[ciphername]).intersection(set(available_modules[ciphername])))
		#print('possible_prefmodule %s' % possible_prefmodule)
		selected_module = None
		for moduleName in preftable[ciphername]:
			if moduleName in possible_prefmodule:
				selected_module = moduleName
				break

		if selected_module is None:
			raise Exception('Could not find any modules to load cipher "%s"' % ciphername)
	else:
		selected_module = override_library
	
	#print('Preferred module selected for cipher %s is %s' % (ciphername, selected_module))
	return get_cipher_by_name(ciphername, selected_module)

def use_library(libname):
	global override_library
	override_library = libname
