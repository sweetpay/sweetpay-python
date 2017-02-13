"""All tests for the sweetpay package.

These tests can be run with `make test`. But make sure that
you have installed everything in `requirements.txt.dev` first.
This can be accomplished by running `make setupdev`.  Note,
though, that this command assumes that you have `pip` installed
and can use it without root permissions.

Guidelines for writing tests:

Note that we do not make extensive (if any) use of mocks here.
This is because we want to verify that it really works against
the current version of the API. By making use of the real API
it also becomes easier to maintain. However, with that said,
mocks can of course be used in places where the communication
with the API isn't what is being tested.

pytest is king. It is forbidden to write tests with anything
else than pytest, but please feel free to use the patcher
or other helpers from the unittest library.

When writing new tests, always assume that the server is empty,
so that each test can run in whatever order and without prior
setup. This generally means that you need to create new resources
in every.

These tests were originally written while listening to the Weekend
Radio and, at times, Kyla La Grange - Cut Your Teeth on repeat.
"""
