import { ArrowRight, BatteryCharging, Cpu, Gauge, ShieldCheck, Thermometer, Zap } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import type { ExampleProject, Page } from "../types";

export function LandingPage({
  templates,
  onNavigate,
  onTryExample,
}: {
  templates: ExampleProject[];
  onNavigate: (page: Page) => void;
  onTryExample: () => void;
}) {
  const [activeProjectIndex, setActiveProjectIndex] = useState(0);
  const [carouselTransition, setCarouselTransition] = useState(true);
  const featuredProjects = useMemo(() => templates.slice(0, 6), [templates]);
  const carouselProjects = useMemo(
    () => (featuredProjects.length > 1 ? [...featuredProjects, featuredProjects[0]] : featuredProjects),
    [featuredProjects],
  );

  useEffect(() => {
    if (featuredProjects.length <= 1) return;
    const timer = window.setInterval(() => {
      setCarouselTransition(true);
      setActiveProjectIndex((current) => current + 1);
    }, 5000);
    return () => window.clearInterval(timer);
  }, [featuredProjects.length]);

  function handleCarouselTransitionEnd() {
    if (featuredProjects.length > 1 && activeProjectIndex === featuredProjects.length) {
      setCarouselTransition(false);
      setActiveProjectIndex(0);
      window.setTimeout(() => setCarouselTransition(true), 30);
    }
  }

  const features: Array<[string, LucideIcon]> = [
    ["Current Draw Check", Gauge],
    ["Board Reset Risk", Zap],
    ["GPIO Pin Safety", ShieldCheck],
    ["Battery Life Estimate", BatteryCharging],
    ["Regulator Heat Check", Thermometer],
    ["Parts Compatibility Check", Cpu],
    ["Power Path Map", BatteryCharging],
    ["Startup Spike Check", Thermometer],
  ];

  return (
    <main className="animate-page">
      <section className="relative overflow-hidden bg-white/60 text-slate-950 shadow-sm dark:bg-transparent dark:text-white dark:shadow-none">
        <div className="mx-auto grid min-h-[440px] max-w-7xl gap-8 px-6 pb-8 pt-6 sm:px-8 lg:grid-cols-2 lg:items-center lg:px-12 xl:px-14">
          <div className="animate-fade-up">
            <h1 className="text-5xl font-black leading-tight md:text-6xl">PowerCheck AI</h1>
            <p className="mt-5 max-w-2xl text-xl text-slate-950 dark:text-slate-200">
              Design and Validate Your Arduino-Based Power Systems Before You Build
            </p>
            <p className="mt-4 max-w-2xl text-slate-900 dark:text-slate-300">
              Analyze Your Arduino-Based Projects with Current Draw Check, Board Reset Risk, GPIO Pin Safety, Battery
              Life Estimate, Regulator Heat Check, Parts Compatibility Check, Power Path Map, and Startup Spike Check
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <button type="button" className="button-primary bg-cyan-400 text-slate-950 hover:bg-cyan-300" onClick={() => onNavigate("builder")}>
                Start New Analysis
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
          <div className="animate-scale-in">
            <div
              className="cursor-pointer rounded-lg border border-cyan-200 bg-white p-5 shadow-[0_14px_34px_rgba(15,23,42,0.16),0_0_18px_rgba(34,211,238,0.12)] transition duration-200 ease-out hover:-translate-y-0.5 hover:bg-white active:translate-y-0 active:scale-95 dark:border-cyan-400/30 dark:bg-slate-950 dark:shadow-[0_0_0_1px_rgba(34,211,238,0.2),0_0_24px_rgba(34,211,238,0.22),0_0_64px_rgba(34,211,238,0.14),0_12px_30px_rgba(0,0,0,0.54)] dark:hover:bg-slate-950"
              role="button"
              tabIndex={0}
              onClick={() => featuredProjects.length && onTryExample()}
              onKeyDown={(event) => {
                if ((event.key === "Enter" || event.key === " ") && featuredProjects.length) {
                  event.preventDefault();
                  onTryExample();
                }
              }}
            >
            <div className="mb-3 inline-flex rounded-full border border-cyan-200 bg-cyan-50 px-3 py-1 text-xs font-bold uppercase tracking-normal text-slate-950 dark:border-cyan-400/40 dark:bg-cyan-400/10 dark:text-cyan-100">
              Starter Projects
            </div>
            <div className="overflow-hidden rounded-md border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
              <div
                className={`flex ${carouselTransition ? "carousel-slide" : ""}`}
                style={{ transform: `translateX(-${activeProjectIndex * 100}%)` }}
                onTransitionEnd={handleCarouselTransitionEnd}
              >
                {carouselProjects.map((project, index) => (
                  <button
                    key={`${project.id}-${index}`}
                    type="button"
                    className="w-full shrink-0 p-4 text-left transition duration-300 ease-out hover:bg-cyan-50 active:scale-[0.99] dark:hover:bg-slate-800/40"
                    onClick={() => onTryExample()}
                    aria-label={`Try ${project.name}`}
                  >
                    <div className="flex items-center justify-between border-b border-slate-200 pb-3 dark:border-slate-700">
                      <div>
                        <div className="text-2xl font-bold">{project.name}</div>
                      </div>
                      <div className={`rounded-full px-3 py-1 text-sm font-bold ${ratingTone(projectScore(project.name))}`}>
                        Rating: {projectScore(project.name)}/100
                      </div>
                    </div>
                    <p className="mt-4 min-h-12 text-sm leading-6 text-slate-950 dark:text-slate-300">{project.description}</p>
                    <div className="mt-4 grid gap-3 sm:grid-cols-2">
                      {featureSetForSlide(index, features).map((item) => (
                          <div key={item} className="rounded-md bg-slate-50 p-3 text-sm text-slate-950 dark:bg-slate-800 dark:text-slate-200">
                            {item}
                          </div>
                        ))}
                    </div>
                  </button>
                ))}
              </div>
            </div>
            <div className="mt-4 flex justify-center gap-2">
              {featuredProjects.map((project, index) => (
                <button
                  key={project.id}
                  type="button"
                  className={`h-2.5 rounded-full transition-all duration-300 active:scale-90 ${
                    activeProjectIndex % featuredProjects.length === index
                      ? "w-8 bg-cyan-300"
                      : "w-2.5 bg-slate-300 hover:bg-slate-400 dark:bg-white/30 dark:hover:bg-white/60"
                  }`}
                  onClick={(event) => {
                    event.stopPropagation();
                    setCarouselTransition(true);
                    setActiveProjectIndex(index);
                  }}
                  aria-label={`Show ${project.name}`}
                />
              ))}
            </div>
            </div>
          </div>
        </div>
      </section>
      <section className="mx-auto max-w-7xl px-6 pb-10 pt-6 sm:px-8 lg:px-12 xl:px-14">
        <div className="mb-5">
          <h2 className="text-2xl font-black text-slate-950 dark:text-white">Features</h2>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {features.map(([label, Icon]) => (
            <div key={label} className="panel animate-fade-up-delay p-4">
              <Icon className="h-5 w-5 text-cyan-600" />
              <div className="mt-3 text-sm font-semibold text-slate-950 dark:text-white">{label}</div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

function ratingTone(score: number): string {
  if (score >= 70) {
    return "bg-green-100 text-green-900 ring-1 ring-green-300 dark:bg-green-400/15 dark:text-green-100 dark:ring-green-300/30";
  }
  if (score >= 30) {
    return "bg-yellow-100 text-yellow-900 ring-1 ring-yellow-300 dark:bg-yellow-400/15 dark:text-yellow-100 dark:ring-yellow-300/30";
  }
  return "bg-red-100 text-red-900 ring-1 ring-red-300 dark:bg-red-400/15 dark:text-red-100 dark:ring-red-300/30";
}

function projectScore(name: string): number {
  const scores: Record<string, number> = {
    "Home Weather Station": 94,
    "Digital Alarm Clock with OLED Display": 92,
    "Wi-Fi Smart Home Controller": 88,
    "ESP32 Security Camera System": 84,
    "Bluetooth RC Car": 78,
    "Line Following Robot": 76,
    "Smart Plant Watering System": 72,
    "RFID Door Lock System": 68,
    "Ultrasonic Obstacle Avoiding Robot": 66,
    "LED Music Visualizer": 58,
  };
  return scores[name] ?? 75;
}

function featureSetForSlide(index: number, features: Array<[string, LucideIcon]>): string[] {
  if (!features.length) return [];
  const step = 3;
  const start = (index * step) % features.length;
  return Array.from({ length: 4 }, (_, offset) => features[(start + offset) % features.length][0]);
}
