"""
Remote services integration layer, including:
* Platform model/app dependencies
* App API integrations
* Direct model integrations (where necessary)
* Non-signal framework data dependencies
* Remote services/systems integrations

Basically any interactions with the system outside of internal application
state, which is handled in models.py

This module should only be called directly by data.py, in order to
maintain the intended data layer abstractions/contracts.
"""
