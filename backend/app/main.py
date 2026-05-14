from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from app.analysis_engine import analyze_project, calculate_battery_life, calculate_regulator_heat, component_current
from app.database import SessionLocal, get_db, init_db
from app.models import Component, ExampleProject, PowerSource, Regulator
from app.project_parser import parse_project_description
from app.recommendations import explain_warnings, top_fixes
from app.report_generator import generate_text_report
from app.schemas import (
    AnalyzeRequest,
    BatteryLifeEstimateRequest,
    ComponentRead,
    ExampleProjectRead,
    GenerateReportRequest,
    NeoPixelEstimateRequest,
    PowerSourceRead,
    ProjectDescriptionRequest,
    RegulatorHeatEstimateRequest,
    RegulatorRead,
)
from app.services.ai_analysis.project_text_analyzer import analyze_project_description_text
from app.services.ai_analysis.schemas import AnalyzeProjectDescriptionRequest, AnalyzeProjectDescriptionResponse
from app.seed_data import EXAMPLE_PROJECTS, seed_database


def ensure_seed_data() -> None:
    init_db()
    db = SessionLocal()
    try:
        has_missing_lookup_data = (
            db.query(Component).count() == 0
            or db.query(PowerSource).count() == 0
            or db.query(Regulator).count() == 0
            or db.query(ExampleProject).count() == 0
        )
        current_example_names = {name for (name,) in db.query(ExampleProject.name).all()}
        seeded_example_names = {project["name"] for project in EXAMPLE_PROJECTS}
        has_old_example_projects = current_example_names != seeded_example_names
        if has_missing_lookup_data or has_old_example_projects:
            seed_database(db)
    finally:
        db.close()


def model_to_dict(model) -> dict:
    return {
        column.name: getattr(model, column.name)
        for column in model.__table__.columns
    }


def get_component_or_404(db: Session, component_id: int) -> Component:
    component = db.get(Component, component_id)
    if component is None:
        raise HTTPException(status_code=404, detail=f"Component {component_id} not found")
    return component


def get_power_source_or_404(db: Session, power_source_id: int) -> PowerSource:
    power_source = db.get(PowerSource, power_source_id)
    if power_source is None:
        raise HTTPException(status_code=404, detail=f"Power source {power_source_id} not found")
    return power_source


def get_regulator_or_404(db: Session, regulator_id: int) -> Regulator:
    regulator = db.get(Regulator, regulator_id)
    if regulator is None:
        raise HTTPException(status_code=404, detail=f"Regulator {regulator_id} not found")
    return regulator


def build_analysis_inputs(payload: AnalyzeRequest, db: Session) -> dict:
    microcontroller = model_to_dict(get_component_or_404(db, payload.selected_microcontroller_id))
    selected_components = []
    for selected in payload.selected_components:
        component = model_to_dict(get_component_or_404(db, selected.component_id))
        selected_components.append(
            {
                "component": component,
                "quantity": selected.quantity,
                "powered_from": selected.powered_from,
                "rail_voltage": selected.rail_voltage,
            }
        )

    if payload.custom_power_source is not None:
        power_source = payload.custom_power_source.model_dump()
    elif payload.selected_power_source_id is not None:
        power_source = model_to_dict(get_power_source_or_404(db, payload.selected_power_source_id))
    else:
        raise HTTPException(status_code=400, detail="Select a power source or provide custom_power_source")

    regulator = model_to_dict(get_regulator_or_404(db, payload.regulator_id)) if payload.regulator_id else None

    return {
        "microcontroller": microcontroller,
        "selected_components": selected_components,
        "power_source": power_source,
        "regulator": regulator,
        "settings": payload.settings.model_dump(),
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_seed_data()
    yield


app = FastAPI(
    title="PowerCheck AI API",
    description="Backend API for Arduino and ESP32 power validation.",
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/components", response_model=list[ComponentRead])
def get_components(
    category: str | None = Query(default=None, description="Optional component category filter."),
    db: Session = Depends(get_db),
) -> list[Component]:
    query = db.query(Component)
    if category:
        query = query.filter(Component.category == category)
    return query.order_by(Component.category, Component.name).all()


@app.get("/power-sources", response_model=list[PowerSourceRead])
def get_power_sources(db: Session = Depends(get_db)) -> list[PowerSource]:
    return db.query(PowerSource).order_by(PowerSource.source_type, PowerSource.name).all()


@app.get("/regulators", response_model=list[RegulatorRead])
def get_regulators(db: Session = Depends(get_db)) -> list[Regulator]:
    return db.query(Regulator).order_by(Regulator.regulator_type, Regulator.name).all()


@app.get("/example-projects", response_model=list[ExampleProjectRead])
def get_example_projects(db: Session = Depends(get_db)) -> list[ExampleProject]:
    return db.query(ExampleProject).order_by(ExampleProject.id).all()


@app.post("/analyze")
def analyze(payload: AnalyzeRequest, db: Session = Depends(get_db)) -> dict:
    inputs = build_analysis_inputs(payload, db)
    analysis = analyze_project(
        inputs["microcontroller"],
        inputs["selected_components"],
        inputs["power_source"],
        inputs["regulator"],
        inputs["settings"],
    )
    return {
        **analysis,
        "selected_microcontroller": inputs["microcontroller"],
        "selected_components": inputs["selected_components"],
        "power_source": inputs["power_source"],
        "regulator": inputs["regulator"],
        "explanations": explain_warnings(analysis["warnings"]),
        "top_fixes": top_fixes(analysis["warnings"]),
    }


@app.post("/analyze-project-description", response_model=AnalyzeProjectDescriptionResponse)
def analyze_project_description(payload: AnalyzeProjectDescriptionRequest, db: Session = Depends(get_db)) -> dict:
    return analyze_project_description_text(
        project_name=payload.project_name,
        description_text=payload.description_text,
        components=db.query(Component).order_by(Component.category, Component.name).all(),
        power_sources=db.query(PowerSource).order_by(PowerSource.source_type, PowerSource.name).all(),
        regulators=db.query(Regulator).order_by(Regulator.regulator_type, Regulator.name).all(),
        existing_project_config=payload.existing_project_config,
    )


@app.post("/parse-project-description")
def parse_project(payload: ProjectDescriptionRequest) -> dict:
    return parse_project_description(payload.description)


@app.post("/generate-report")
def generate_report(payload: GenerateReportRequest, db: Session = Depends(get_db)) -> dict:
    inputs = build_analysis_inputs(payload, db)
    analysis = analyze_project(
        inputs["microcontroller"],
        inputs["selected_components"],
        inputs["power_source"],
        inputs["regulator"],
        inputs["settings"],
    )
    report_components = [
        {"component": inputs["microcontroller"], "quantity": 1},
        *inputs["selected_components"],
    ]
    report = generate_text_report(payload.project_name, analysis, report_components, inputs["power_source"])
    return {
        "project_name": payload.project_name,
        "report": report,
        "risk": analysis["risk"],
    }


@app.post("/estimate-neopixel-current")
def estimate_neopixel_current(payload: NeoPixelEstimateRequest) -> dict:
    neopixel = {
        "name": "NeoPixel Strip",
        "category": "led",
        "typical_current_mA": 20,
        "max_current_mA": 60,
    }
    current = component_current(
        neopixel,
        quantity=payload.led_count,
        settings={"brightness_percent": payload.brightness_percent},
    )
    return {
        "led_count": payload.led_count,
        "brightness_percent": payload.brightness_percent,
        "typical_current_mA": current["typical_mA"],
        "max_current_mA": current["peak_mA"],
        "recommended_supply_current_mA": round(current["peak_mA"] * 1.2, 2),
    }


@app.post("/estimate-regulator-heat")
def estimate_regulator_heat(payload: RegulatorHeatEstimateRequest) -> dict:
    regulator = {
        "name": f"Custom {payload.regulator_type.title()} Regulator",
        "regulator_type": payload.regulator_type,
        "efficiency": payload.efficiency,
    }
    if payload.regulator_type == "buck" and regulator["efficiency"] is None:
        regulator["efficiency"] = 0.9
    if payload.regulator_type == "boost" and regulator["efficiency"] is None:
        regulator["efficiency"] = 0.85
    return calculate_regulator_heat(
        regulator,
        input_voltage=payload.input_voltage,
        output_voltage=payload.output_voltage,
        output_current_mA=payload.output_current_mA,
    )


@app.post("/estimate-battery-life")
def estimate_battery_life(payload: BatteryLifeEstimateRequest) -> dict:
    power_source = {
        "name": "Custom Battery",
        "voltage": 0,
        "max_current_mA": 0,
        "capacity_mAh": payload.capacity_mAh,
        "source_type": "battery",
    }
    peak_current = payload.peak_current_mA or payload.typical_current_mA
    return calculate_battery_life(
        power_source,
        typical_current_mA=payload.typical_current_mA,
        peak_current_mA=peak_current,
        efficiency=payload.efficiency,
    )
