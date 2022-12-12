from app.controller import transpile, execute, calculation, benchmark, analysis, analysis_original_circuit, wd_calc

MODULES = (transpile, execute, calculation, benchmark, analysis, analysis_original_circuit, wd_calc)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        api.register_blueprint(module.blp)
