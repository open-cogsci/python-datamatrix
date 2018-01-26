# -*- coding: utf-8 -*-

"""
This file is part of datamatrix.

datamatrix is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

datamatrix is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with datamatrix.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import hashlib
import pickle
import shutil


class memoize(object):

	"""
	desc: |
		A memoization decorator that stores the result of a function call, and
		returns the stored value when the function is called again with the same
		arguments. That is, memoization is a specific kind of caching that
		improves performance for expensive function calls.

		This decorator only works for arguments and return values
		that can be serialized (i.e. arguments that you can pickle).

		The memoized function becomes a callable object. To clear the
		memoization cache, call the `.clear()` function on the memoized
		function.

		For a more detailed description, see:

		- %link:memoization%

		*Changed in v0.8.0*: You can no longer pass the `memoclear` keyword to
		the memoized function.

		__Example:__

		%--
		python: |
		 from datamatrix import functional as fnc

		 @fnc.memoize
		 def add(a, b):

		 	print('add(%d, %d)' % (a, b))
		 	return a + b

		 three = add(1, 2) # Storing result in memory
		 three = add(1, 2) # Re-using previous result
		 add.clear() # Clear cache!
		 three = add(1, 2) # Calculate again

		 @fnc.memoize(persistent=True, key='persistent-add')
		 def persistent_add(a, b):

		 	print('persistent_add(%d, %d)' % (a, b))
		 	return a + b

		 three = persistent_add(1, 2) # Writing result to disk
		 three = persistent_add(1, 2) # Re-using previous result
		--%

	keywords:
		fnc:
			desc:	A function to memoize.
			type:	callable
		persistent:
			desc:	Indicates whether the result should be written to disk so
					that the result can be re-used when the script is run again.
					If set to `True`, the result is stored as a pickle in a
					`.memoize` subfolder of the working directory.
			type:	bool
		key:
			desc:	Indicates a key that identifies the results. If no key is
					provided, a key is generated based on the function name,
					and the arguments passed to the function. However, this
					requires the arguments to be serialized, which can take some
					time.
			type:	[str, None]
		lazy:
			desc:	If `True`, any callable that is passed onto the memoized
					function is automatically called, and the memoized function
					receives the return value instead of the function object.
					This allows for lazy evaluation.
			type:	bool
		debug:
			desc:	If `True`, the memoized function returns a
					`(retval, memkey, source)` tuple, where `retval` is the
					function's return value, `memkey` is the key used for
					caching, and `source` is one of 'memory', 'disk', or
					'function', indicating whether and how the return value was
					cached. This is mostly for debugging and testing.
			type:	bool

	returns:
		desc:	A memoized version of fnc.
		type:	callable
	"""

	def __init__(
		self, fnc=None, key=None, persistent=False, lazy=False, debug=False,
		folder=u'.memoize'
	):

		self._fnc = fnc
		self._key = key
		self._persistent = persistent
		self._lazy = lazy
		self._debug = debug
		self._folder = folder
		self._init_cache()

	def clear(self):

		if self._persistent and os.path.exists(self._folder):
			shutil.rmtree(self._folder)
		self._init_cache()

	@property
	def __call__(self):

		return (
			self._call_with_arguments
			if self._fnc is None
			else self._call_without_arguments
		)

	def _call_with_arguments(self, fnc):

		return self.__class__(
			fnc,
			key=self._key,
			persistent=self._persistent,
			lazy=self._lazy,
			debug=self._debug,
			folder=self._folder
		)

	def _call_without_arguments(self, *args, **kwargs):

		memkey = (
			self._memkey(*args, **kwargs)
			if self._key is None else self._key
		)
		is_cached, retval = self._read_cache(memkey)
		if is_cached:
			return (
				(retval, memkey, self._latest_source)
				if self._debug
				else retval
			)
		if self._lazy:
			args, kwargs = self._lazy_evaluation(args, kwargs)
		return self._write_cache(
			memkey,
			self._fnc(*args, **kwargs)
		)

	def _lazy_evaluation(self, args, kwargs):

		return (
			[
				arg() if callable(arg) else arg
				for arg in args
			],
			{
				key: val() if callable(val) else val
				for key, val in kwargs.items()
			}
		)

	def _init_cache(self):

		self._cache = {}
		if self._persistent and not os.path.exists(self._folder):
			os.mkdir(self._folder)

	def _read_cache(self, memkey):

		if memkey in self._cache:
			self._latest_source = 'memory'
			return True, pickle.loads(self._cache[memkey])
		if self._persistent:
			cache_path = os.path.join(self._folder, memkey)
			if os.path.exists(cache_path):
				self._latest_source = 'disk'
				with open(cache_path, u'rb') as fd:
					return True, pickle.load(fd)
		self._latest_source = 'function'
		return False, None

	def _write_cache(self, memkey, retval):

		self._cache[memkey] = pickle.dumps(retval)
		if self._persistent:
			cache_path = os.path.join(self._folder, memkey)
			if not os.path.exists(cache_path):
				with open(cache_path, u'wb') as fd:
					pickle.dump(retval, fd)
		return (
			(retval, memkey, self._latest_source)
			if self._debug
			else retval
		)

	def _memkey(self, *args, **kwdict):

		args = [
			(arg.__name__ if hasattr(arg, '__name') else '__nameless__')
			if callable(arg) else arg for arg in args
		]
		return hashlib.md5(
			pickle.dumps([self._fnc.__name__, args, kwdict])
		).hexdigest()