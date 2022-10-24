from app.controller import transpile, execute, calculation, benchmark, analysis

MODULES = (transpile, execute, calculation, benchmark, analysis)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        api.register_blueprint(module.blp)
