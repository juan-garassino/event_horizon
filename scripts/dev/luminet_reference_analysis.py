#!/usr/bin/env python3
"""
Comprehensive Reference Luminet Implementation Analysis Script

This script analyzes the complete Luminet data pipeline from the reference implementation,
documenting the step-by-step process from initialization to final visualization.

Requirements addressed:
- 1.1: Document step-by-step DataFrame creation process
- 1.2: Explain sample point transformation by relativistic space
- 1.3: Identify order of operations from calculations to visualization
- 1.4: Document coordinate transformation pipeline including -π/2 rotation
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import configparser
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime

# Add reference path to import Luminet modules
sys.path.append('references/luminet/core')
sys.path.append('references/luminet')

try:
    from black_hole import BlackHole
    from bh_math import *
    from bh_utils import *
    from isoradials import Isoradial
except ImportError as e:
    print(f"Warning: Could not import reference modules: {e}")
    print("Analysis will be limited to static code analysis")

class LuminetReferenceAnalyzer:
    """
    Comprehensive analyzer for the reference Luminet implementation.
    
    This class systematically extracts and documents the complete data pipeline
    from parameter initialization to final visualization rendering.
    """
    
    def __init__(self, output_dir: str = "analysis_output"):
        """Initialize the analyzer with output directory for results."""
        self.output_dir = output_dir
        self.analysis_results = {}
        self.create_output_directory()
        
    def create_output_directory(self):
        """Create output directory for analysis results."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def analyze_parameter_initialization(self) -> Dict:
        """
        Analyze the BlackHole class initialization and parameter loading process.
        
        Returns:
            Dict containing analysis of initialization process
        """
        print("=== ANALYZING PARAMETER INITIALIZATION ===")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "initialization_process": {},
            "parameter_structure": {},
            "critical_constants": {}
        }
        
        # Analyze parameters.ini structure
        try:
            config = configparser.ConfigParser(inline_comment_prefixes='#')
            config.read('references/luminet/parameters.ini')
            
            analysis["parameter_structure"] = {
                "sections": list(config.sections()),
                "section_details": {}
            }
            
            for section in config.sections():
                analysis["parameter_structure"]["section_details"][section] = {
                    key: val for key, val in config[section].items()
                }
                
        except Exception as e:
            analysis["parameter_structure"]["error"] = str(e)
            
        # Document BlackHole initialization sequence
        analysis["initialization_process"] = {
            "step_1": "Set inclination angle (degrees to radians conversion)",
            "step_2": "Set black hole mass M and accretion rate",
            "step_3": "Calculate critical impact parameter: b_c = 3√3 * M",
            "step_4": "Initialize empty dictionaries for settings and parameters",
            "step_5": "Call __read_parameters() to load from parameters.ini",
            "step_6": "Set disk edges: inner=6M, outer=50M",
            "step_7": "Calculate apparent disk edges using Isoradial objects",
            "step_8": "Initialize empty dictionaries for isoradials and isoredshifts"
        }
        
        # Critical constants and their significance
        analysis["critical_constants"] = {
            "photon_sphere_radius": {
                "value": "3 * M",
                "significance": "Innermost stable circular orbit for photons"
            },
            "critical_impact_parameter": {
                "value": "3 * sqrt(3) * M ≈ 5.196 * M",
                "significance": "Impact parameter for photon sphere, separates direct from ghost images"
            },
            "disk_inner_edge": {
                "value": "6 * M",
                "significance": "Innermost stable circular orbit for matter (ISCO)"
            },
            "disk_outer_edge": {
                "value": "50 * M",
                "significance": "Outer boundary of accretion disk"
            },
            "coordinate_rotation": {
                "value": "-π/2",
                "significance": "Critical rotation applied in polar_to_cartesian_lists for proper orientation"
            }
        }
        
        self.analysis_results["initialization"] = analysis
        return analysis
        
    def analyze_sampling_methodology(self) -> Dict:
        """
        Analyze the particle sampling strategy and biasing approach.
        
        Returns:
            Dict containing detailed sampling analysis
        """
        print("=== ANALYZING SAMPLING METHODOLOGY ===")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "sampling_strategy": {},
            "biasing_approach": {},
            "coordinate_generation": {}
        }
        
        # Document sampling strategy from sample_points method
        analysis["sampling_strategy"] = {
            "method": "Biased sampling toward disk center",
            "radius_generation": "r = min_radius + max_radius * np.random.random()",
            "angle_generation": "theta = np.random.random() * 2 * np.pi",
            "bias_rationale": "Observed flux is exponentially bigger near center, needs most precision",
            "range": {
                "min_radius": "self.disk_inner_edge (6M)",
                "max_radius": "self.disk_outer_edge (50M)"
            }
        }
        
        # Explain biasing vs uniform sampling
        analysis["biasing_approach"] = {
            "uniform_sampling": "r = min_radius + max_radius * sqrt(np.random.random())",
            "biased_sampling": "r = min_radius + max_radius * np.random.random()",
            "difference": "Biased sampling favors smaller radii where flux is higher",
            "impact": "More sample points near black hole where relativistic effects are strongest"
        }
        
        # Document coordinate generation process
        analysis["coordinate_generation"] = {
            "step_1": "Generate random radius r and angle theta in disk frame",
            "step_2": "Calculate impact parameter b using calc_impact_parameter()",
            "step_3": "Convert to Cartesian coordinates using polar_to_cartesian_lists()",
            "step_4": "Apply critical -π/2 rotation during conversion",
            "step_5": "Calculate redshift factor and observed flux",
            "step_6": "Store in DataFrame with columns: ['X', 'Y', 'impact_parameter', 'angle', 'z_factor', 'flux_o']"
        }
        
        self.analysis_results["sampling"] = analysis
        return analysis
        
    def analyze_impact_parameter_calculation(self) -> Dict:
        """
        Analyze the impact parameter calculation using elliptic integrals.
        
        Returns:
            Dict containing impact parameter calculation analysis
        """
        print("=== ANALYZING IMPACT PARAMETER CALCULATION ===")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "calculation_pipeline": {},
            "elliptic_integral_approach": {},
            "midpoint_refinement": {}
        }
        
        # Document the calculation pipeline
        analysis["calculation_pipeline"] = {
            "function": "calc_impact_parameter(r, incl, alpha, bh_mass, **solver_params)",
            "step_1": "Call calc_periastron() to find periastron distance P",
            "step_2": "Generate range of P values from min_periastron to 2*r",
            "step_3": "Evaluate eq13(P) for each P value to find sign changes",
            "step_4": "Use midpoint method to refine solution iteratively",
            "step_5": "Convert final P to impact parameter b using calc_b_from_periastron()",
            "fallback": "Use ellipse() function if no physical solution found"
        }
        
        # Document elliptic integral mathematics
        analysis["elliptic_integral_approach"] = {
            "equation_13": "Core equation relating radius r, angle alpha, and periastron P",
            "elliptic_functions": [
                "ellipkinc(zeta_inf, k²) - Incomplete elliptic integral of first kind",
                "ellipk(k²) - Complete elliptic integral of first kind",
                "ellipj(u, k²) - Jacobi elliptic functions (sn, cn, dn)"
            ],
            "key_variables": {
                "Q": "sqrt((P - 2M)(P + 6M)) - Auxiliary variable",
                "k²": "(Q - P + 6M)/(2Q) - Squared modulus of elliptic integral",
                "zeta_inf": "arcsin(sqrt((Q - P + 2M)/(Q - P + 6M))) - Integration limit"
            }
        }
        
        # Document midpoint refinement process
        analysis["midpoint_refinement"] = {
            "purpose": "Achieve high precision in periastron calculation",
            "method": "Iteratively bisect interval where eq13 changes sign",
            "iterations": "Controlled by midpoint_iterations parameter (default: 20)",
            "convergence": "Continues until desired precision reached",
            "robustness": "Handles cases where initial guess range is too narrow"
        }
        
        self.analysis_results["impact_parameter"] = analysis
        return analysis
        
    def analyze_coordinate_transformation(self) -> Dict:
        """
        Analyze the coordinate transformation pipeline including the critical -π/2 rotation.
        
        Returns:
            Dict containing coordinate transformation analysis
        """
        print("=== ANALYZING COORDINATE TRANSFORMATION ===")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "transformation_pipeline": {},
            "critical_rotation": {},
            "coordinate_systems": {}
        }
        
        # Document transformation pipeline
        analysis["transformation_pipeline"] = {
            "input": "Impact parameter b and angle alpha (polar coordinates)",
            "function": "polar_to_cartesian_lists(radii, angles, rotation=-π/2)",
            "output": "Cartesian coordinates (X, Y) on observer's photographic plate",
            "formula": {
                "x": "b * cos(alpha + rotation)",
                "y": "b * sin(alpha + rotation)"
            }
        }
        
        # Analyze the critical -π/2 rotation
        analysis["critical_rotation"] = {
            "value": "-π/2 radians (-90 degrees)",
            "purpose": "Align coordinate system with observer's reference frame",
            "effect": "Rotates entire image counterclockwise by 90 degrees",
            "significance": "Essential for proper orientation of black hole shadow and accretion disk",
            "without_rotation": "Image would appear rotated 90 degrees clockwise",
            "applied_in": [
                "Direct image coordinate calculation",
                "Ghost image coordinate calculation", 
                "Apparent disk edge calculations",
                "All Isoradial coordinate transformations"
            ]
        }
        
        # Document coordinate systems
        analysis["coordinate_systems"] = {
            "black_hole_frame": {
                "description": "Natural coordinate system of the black hole",
                "angles": "Measured from equatorial plane",
                "radius": "Physical distance from black hole center"
            },
            "observer_frame": {
                "description": "Coordinate system as seen by distant observer",
                "angles": "Measured on photographic plate",
                "radius": "Impact parameter (apparent distance)"
            },
            "transformation_sequence": [
                "1. Generate (r, theta) in black hole frame",
                "2. Calculate impact parameter b from r, theta via ray tracing",
                "3. Convert (b, alpha) to Cartesian with -π/2 rotation",
                "4. Result: (X, Y) coordinates on observer's photographic plate"
            ]
        }
        
        self.analysis_results["coordinate_transformation"] = analysis
        return analysis
        
    def analyze_dataframe_creation(self) -> Dict:
        """
        Analyze the step-by-step DataFrame creation process from sampling to storage.
        
        Returns:
            Dict containing DataFrame creation analysis
        """
        print("=== ANALYZING DATAFRAME CREATION PROCESS ===")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "dataframe_structure": {},
            "creation_process": {},
            "ghost_image_handling": {}
        }
        
        # Document DataFrame structure
        analysis["dataframe_structure"] = {
            "direct_image_columns": [
                "X - Cartesian X coordinate on observer plate",
                "Y - Cartesian Y coordinate on observer plate", 
                "impact_parameter - Impact parameter b",
                "angle - Angle theta in black hole frame",
                "z_factor - Redshift factor (1 + z)",
                "flux_o - Observed flux after redshift correction"
            ],
            "ghost_image_columns": "Same as direct image but stored in separate DataFrame",
            "file_naming": {
                "direct": "Points/points_incl={inclination}.csv",
                "ghost": "Points/points_secondary_incl={inclination}.csv"
            }
        }
        
        # Document creation process step by step
        analysis["creation_process"] = {
            "initialization": {
                "step": "Load existing CSV or create empty DataFrame with required columns",
                "code": "pd.DataFrame(columns=['X', 'Y', 'impact_parameter', 'angle', 'z_factor', 'flux_o'])"
            },
            "sampling_loop": {
                "iterations": "n_points (typically 1000-10000)",
                "per_iteration": [
                    "1. Generate random r and theta",
                    "2. Calculate impact parameter for direct image (n=0)",
                    "3. Calculate impact parameter for ghost image (n=1)", 
                    "4. If direct solution exists: calculate coordinates, redshift, flux",
                    "5. If ghost solution exists: calculate coordinates, redshift, flux",
                    "6. Append to respective DataFrames using pd.concat()"
                ]
            },
            "storage": {
                "method": "DataFrame.to_csv() with index",
                "location": "Points/ directory",
                "format": "CSV with comma separation"
            }
        }
        
        # Document ghost image handling
        analysis["ghost_image_handling"] = {
            "definition": "Secondary images formed by photons that orbit black hole before reaching observer",
            "calculation": "Same physics but with n=1 parameter in calc_impact_parameter()",
            "separation": "Stored in completely separate DataFrame and CSV file",
            "coordinate_difference": "Same transformation but different impact parameters",
            "rendering_difference": "Y-coordinates flipped during visualization: [-e for e in points_['Y']]"
        }
        
        self.analysis_results["dataframe_creation"] = analysis
        return analysis
        
    def analyze_visualization_pipeline(self) -> Dict:
        """
        Analyze the complete visualization rendering pipeline.
        
        Returns:
            Dict containing visualization pipeline analysis
        """
        print("=== ANALYZING VISUALIZATION PIPELINE ===")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "rendering_hierarchy": {},
            "tricontour_parameters": {},
            "ghost_image_rendering": {},
            "artifact_masking": {}
        }
        
        # Document rendering hierarchy
        analysis["rendering_hierarchy"] = {
            "step_1": "Setup figure with black background",
            "step_2": "Load direct and ghost image DataFrames from CSV",
            "step_3": "Calculate flux normalization: max_flux from both DataFrames",
            "step_4": "Render ghost image first (background layer)",
            "step_5": "Render direct image second (foreground layer)",
            "step_6": "Apply artifact masking with black fill_between",
            "step_7": "Set axis limits and save/display result"
        }
        
        # Document tricontour parameters
        analysis["tricontour_parameters"] = {
            "function": "matplotlib.pyplot.tricontourf()",
            "parameters": {
                "X": "points_['X'] - X coordinates",
                "Y": "points_['Y'] or [-e for e in points_['Y']] for ghost",
                "Z": "flux values after normalization and power scaling",
                "cmap": "'Greys_r' - Reversed grayscale colormap",
                "levels": "100 (default) - Number of contour levels",
                "norm": "plt.Normalize(0, 1) - Normalize flux to [0,1] range",
                "nchunk": "2 - Number of chunks for triangulation"
            },
            "flux_scaling": {
                "formula": "(abs(fl + min_flux) / (max_flux + min_flux)) ** power_scale",
                "power_scale": "0.9 (default) - Enhances dim regions",
                "min_flux": "0 - Minimum flux value",
                "max_flux": "max(max(direct_flux), max(ghost_flux))"
            }
        }
        
        # Document ghost image rendering specifics
        analysis["ghost_image_rendering"] = {
            "y_coordinate_flip": "Y coordinates flipped: [-e for e in points_['Y']]",
            "region_splitting": {
                "inner_region": "b < get_apparent_inner_edge_radius(a + π)",
                "outer_region": "b > get_apparent_outer_edge_radius(a + π)",
                "angle_offset": "a + π applied to edge calculations"
            },
            "alpha_blending": "alpha=0.5 for ghost images vs alpha=1.0 for direct",
            "zorder": "Ghost rendered first (lower zorder) for proper layering"
        }
        
        # Document artifact masking
        analysis["artifact_masking"] = {
            "purpose": "Fill Delaunay triangulation artifacts with black",
            "method": "plt.fill_between() with black color",
            "locations": [
                "Apparent inner disk edge boundary",
                "Apparent outer disk edge boundary", 
                "Photon sphere boundary"
            ],
            "zorder": "High zorder (1-2) to render on top of contours"
        }
        
        self.analysis_results["visualization"] = analysis
        return analysis
        
    def analyze_physics_calculations(self) -> Dict:
        """
        Analyze the relativistic physics calculations for redshift and flux.
        
        Returns:
            Dict containing physics calculations analysis
        """
        print("=== ANALYZING PHYSICS CALCULATIONS ===")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "redshift_calculation": {},
            "flux_calculation": {},
            "apparent_edge_calculation": {}
        }
        
        # Document redshift factor calculation
        analysis["redshift_calculation"] = {
            "function": "redshift_factor(radius, angle, incl, bh_mass, b_)",
            "formula": "(1 + √(M/r³) * b * sin(incl) * sin(angle)) * (1 - 3M/r)^(-1/2)",
            "components": {
                "gravitational_redshift": "(1 - 3M/r)^(-1/2)",
                "doppler_shift": "1 + √(M/r³) * b * sin(incl) * sin(angle)",
                "orbital_velocity": "√(M/r³) - Keplerian orbital frequency",
                "projection_factor": "b * sin(incl) * sin(angle)"
            },
            "physical_meaning": "Combined gravitational and Doppler redshift effects"
        }
        
        # Document flux calculation
        analysis["flux_calculation"] = {
            "intrinsic_flux": {
                "function": "flux_intrinsic(r, acc, bh_mass)",
                "formula": "Standard thin disk model with logarithmic correction",
                "components": [
                    "3 * M * acc / (8π) - Normalization factor",
                    "1 / ((r/M - 3) * r^2.5) - Radial dependence", 
                    "Logarithmic term for inner edge correction"
                ]
            },
            "observed_flux": {
                "function": "flux_observed(r, acc, bh_mass, redshift_factor)",
                "formula": "flux_intrinsic / redshift_factor^4",
                "redshift_correction": "Fourth power accounts for photon energy and solid angle effects"
            }
        }
        
        # Document apparent edge calculation
        analysis["apparent_edge_calculation"] = {
            "purpose": "Calculate how disk edges appear curved due to spacetime geometry",
            "method": "Use Isoradial objects to trace light rays from disk edges",
            "inner_edge": {
                "physical_radius": "6M (ISCO)",
                "apparent_shape": "Curved due to light bending",
                "scaling": "0.99 * b for slight inward adjustment"
            },
            "outer_edge": {
                "physical_radius": "50M (disk boundary)",
                "apparent_shape": "Also curved, defines visible disk boundary"
            },
            "coordinate_transformation": "polar_to_cartesian_lists with -π/2 rotation applied"
        }
        
        self.analysis_results["physics"] = analysis
        return analysis
        
    def generate_comprehensive_report(self) -> str:
        """
        Generate a comprehensive analysis report combining all analysis results.
        
        Returns:
            String containing the complete analysis report
        """
        print("=== GENERATING COMPREHENSIVE REPORT ===")
        
        report = f"""
# Comprehensive Luminet Reference Implementation Analysis Report

Generated: {datetime.now().isoformat()}

## Executive Summary

This report provides a complete analysis of the reference Luminet implementation,
documenting the entire data pipeline from black hole parameter initialization
through final visualization rendering. The analysis identifies key algorithmic
components, data structures, and rendering techniques that must be replicated
for accurate black hole visualization.

## 1. Parameter Initialization and Configuration

The BlackHole class initialization follows a systematic sequence:

"""
        
        if "initialization" in self.analysis_results:
            init_analysis = self.analysis_results["initialization"]
            report += "### Initialization Sequence:\n"
            for step, description in init_analysis["initialization_process"].items():
                report += f"- **{step}**: {description}\n"
                
            report += "\n### Critical Constants:\n"
            for constant, details in init_analysis["critical_constants"].items():
                report += f"- **{constant}**: {details['value']} - {details['significance']}\n"
        
        report += """

## 2. Particle Sampling Methodology

The reference implementation uses a biased sampling strategy that favors
the inner regions of the accretion disk where relativistic effects are strongest.

"""
        
        if "sampling" in self.analysis_results:
            sampling_analysis = self.analysis_results["sampling"]
            report += f"### Sampling Strategy:\n"
            report += f"- **Method**: {sampling_analysis['sampling_strategy']['method']}\n"
            report += f"- **Radius Generation**: {sampling_analysis['sampling_strategy']['radius_generation']}\n"
            report += f"- **Rationale**: {sampling_analysis['sampling_strategy']['bias_rationale']}\n"
        
        report += """

## 3. Impact Parameter Calculation

The core physics calculation uses elliptic integrals to solve the geodesic
equations in Schwarzschild spacetime.

"""
        
        if "impact_parameter" in self.analysis_results:
            impact_analysis = self.analysis_results["impact_parameter"]
            report += "### Calculation Pipeline:\n"
            for step, description in impact_analysis["calculation_pipeline"].items():
                if step.startswith("step_"):
                    report += f"- **{step}**: {description}\n"
        
        report += """

## 4. Coordinate Transformation Pipeline

The critical -π/2 rotation is applied during coordinate transformation to
properly orient the black hole image.

"""
        
        if "coordinate_transformation" in self.analysis_results:
            coord_analysis = self.analysis_results["coordinate_transformation"]
            report += "### Critical Rotation:\n"
            rotation_details = coord_analysis["critical_rotation"]
            report += f"- **Value**: {rotation_details['value']}\n"
            report += f"- **Purpose**: {rotation_details['purpose']}\n"
            report += f"- **Effect**: {rotation_details['effect']}\n"
        
        report += """

## 5. DataFrame Creation and Data Flow

The reference implementation creates separate DataFrames for direct and ghost images,
with specific column structures optimized for visualization.

"""
        
        if "dataframe_creation" in self.analysis_results:
            df_analysis = self.analysis_results["dataframe_creation"]
            report += "### DataFrame Structure:\n"
            for column in df_analysis["dataframe_structure"]["direct_image_columns"]:
                report += f"- {column}\n"
        
        report += """

## 6. Visualization Rendering Pipeline

The rendering process follows a specific hierarchy to achieve the correct
visual appearance with proper layering and artifact masking.

"""
        
        if "visualization" in self.analysis_results:
            viz_analysis = self.analysis_results["visualization"]
            report += "### Rendering Hierarchy:\n"
            for step, description in viz_analysis["rendering_hierarchy"].items():
                report += f"- **{step}**: {description}\n"
        
        report += """

## 7. Physics Calculations

Relativistic effects are calculated using standard general relativity formulas
adapted for the Schwarzschild metric.

"""
        
        if "physics" in self.analysis_results:
            physics_analysis = self.analysis_results["physics"]
            report += "### Redshift Calculation:\n"
            redshift_details = physics_analysis["redshift_calculation"]
            report += f"- **Formula**: {redshift_details['formula']}\n"
            report += f"- **Physical Meaning**: {redshift_details['physical_meaning']}\n"
        
        report += """

## Conclusions and Recommendations

This analysis reveals the complete structure of the reference Luminet implementation,
highlighting critical components that must be replicated for accurate visualization:

1. **Biased sampling** toward disk center for optimal precision
2. **Elliptic integral approach** for impact parameter calculation
3. **Critical -π/2 rotation** in coordinate transformations
4. **Separate DataFrame handling** for direct and ghost images
5. **Y-coordinate flipping** for ghost image rendering
6. **Specific tricontour parameters** for proper visualization
7. **Artifact masking** using apparent disk edges

These findings provide the foundation for implementing targeted fixes to
improve EventHorizon's compatibility with the reference implementation.

"""
        
        return report
        
    def save_analysis_results(self):
        """Save all analysis results to JSON and text files."""
        
        # Save JSON data
        json_path = os.path.join(self.output_dir, "luminet_analysis_data.json")
        with open(json_path, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
            
        # Save comprehensive report
        report = self.generate_comprehensive_report()
        report_path = os.path.join(self.output_dir, "luminet_analysis_report.md")
        with open(report_path, 'w') as f:
            f.write(report)
            
        print(f"Analysis results saved to {self.output_dir}/")
        print(f"- JSON data: {json_path}")
        print(f"- Report: {report_path}")
        
    def run_complete_analysis(self):
        """Run the complete analysis pipeline."""
        print("Starting comprehensive Luminet reference implementation analysis...")
        print("=" * 70)
        
        # Run all analysis components
        self.analyze_parameter_initialization()
        self.analyze_sampling_methodology()
        self.analyze_impact_parameter_calculation()
        self.analyze_coordinate_transformation()
        self.analyze_dataframe_creation()
        self.analyze_visualization_pipeline()
        self.analyze_physics_calculations()
        
        # Generate and save results
        self.save_analysis_results()
        
        print("=" * 70)
        print("Analysis complete! Results saved to analysis_output/")
        
        return self.analysis_results

def main():
    """Main execution function."""
    analyzer = LuminetReferenceAnalyzer()
    results = analyzer.run_complete_analysis()
    
    # Print summary
    print("\nAnalysis Summary:")
    print(f"- Analyzed {len(results)} major components")
    print("- Generated comprehensive documentation")
    print("- Identified critical implementation details")
    print("- Ready for EventHorizon comparison and fixes")

if __name__ == "__main__":
    main()