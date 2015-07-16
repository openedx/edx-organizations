"""
Views are listeners connected to the Django HTTP request
pipeline.  When they observe a corresponding URL request they run the
code contained within their definition.

In this particular application, the views simply hand-off to the
orchestration layer, which manages the application's workflows.
"""
