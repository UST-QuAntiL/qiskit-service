from app.controller import transpile, execute, calculation, benchmark, analysis, analysis_original_circuit, wd_calc, \
    provider, result, generated_circuit, generate_circuit

MODULES = (transpile, execute, calculation, benchmark, analysis, analysis_original_circuit, wd_calc, provider, result,
           generated_circuit, generate_circuit)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        api.register_blueprint(module.blp)
