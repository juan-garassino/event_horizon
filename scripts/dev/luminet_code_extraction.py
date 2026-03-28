#!/usr/bin/env python3
"""
Luminet Reference Code Extraction Script

This script extracts and documents the exact code patterns and functions
from the reference Luminet implementation, focusing on the critical
components identified in the main analysis.
"""

import os
import re
from typing import Dict, List

class LuminetCodeExtractor:
    """Extract and document critical code patterns from reference implementation."""
    
    def __init__(self):
        self.extracted_patterns = {}
        
    def extract_coordinate_transformation_code(self) -> Dict:
        """Extract the exact coordinate transformation code patterns."""
        
        patterns = {
            "polar_to_cartesian_function": {
                "file": "references/luminet/core/bh_utils.py",
                "function": "polar_to_cartesian_lists",
                "code": """
def polar_to_cartesian_lists(radii, angles, rotation=0):
    x = []
    y = []
    for R, th in zip(radii, angles):
        x.append(R * np.cos(th + rotation))
        y.append(R * np.sin(th + rotation))
    return x, y
                """,
                "critical_usage": "Always called with rotation=-np.pi/2"
            },
            
            "coordinate_transformation_in_sampling": {
                "file": "references/luminet/core/black_hole.py",
                "location": "sample_points method",
                "code": """
x, y = polar_to_cartesian_lists([b_], [theta], rotation=-np.pi / 2)
                """,
                "significance": "Applied to both direct and ghost images"
            },
            
            "apparent_edge_transformation": {
                "file": "references/luminet/core/black_hole.py", 
                "location": "calc_apparent_inner_disk_edge method",
                "code": """
ir.X, ir.Y = polar_to_cartesian_lists(ir.radii_b, ir.angles, rotation=-np.pi / 2)
                """,
                "significance": "Critical for disk boundary calculations"
            }
        }
        
        return patterns
        
    def extract_sampling_code(self) -> Dict:
        """Extract the exact sampling methodology code."""
        
        patterns = {
            "biased_sampling_loop": {
                "file": "references/luminet/core/black_hole.py",
                "location": "sample_points method",
                "code": """
for _ in t:
    t.update(1)
    theta = np.random.random() * 2 * np.pi
    r = min_radius_ + max_radius_ * np.random.random()  # bias towards center
    b_ = calc_impact_parameter(r, incl=self.t, _alpha=theta, bh_mass=self.M, **self.solver_params)
    b_2 = calc_impact_parameter(r, incl=self.t, _alpha=theta, bh_mass=self.M, **self.solver_params, n=1)
                """,
                "key_points": [
                    "Biased sampling: r = min + max * random() (not sqrt(random()))",
                    "Same r,theta used for both direct (n=0) and ghost (n=1) images",
                    "Separate impact parameter calculations for each image order"
                ]
            },
            
            "dataframe_creation": {
                "file": "references/luminet/core/black_hole.py",
                "location": "sample_points method", 
                "code": """
if b_ is not None:
    x, y = polar_to_cartesian_lists([b_], [theta], rotation=-np.pi / 2)
    redshift_factor_ = redshift_factor(r, theta, self.t, self.M, b_)
    f_o = flux_observed(r, self.acc, self.M, redshift_factor_)
    df = pd.concat([df,
                    pd.DataFrame.from_dict({'X': x, 'Y': y, 'impact_parameter': b_,
                                            'angle': theta,
                                            'z_factor': redshift_factor_, 'flux_o': f_o})])
                """,
                "significance": "Exact DataFrame structure and column names"
            }
        }
        
        return patterns
        
    def extract_visualization_code(self) -> Dict:
        """Extract the exact visualization rendering code."""
        
        patterns = {
            "ghost_image_rendering": {
                "file": "references/luminet/core/black_hole.py",
                "location": "plot_ghost_image function in plot_points method",
                "code": """
def plot_ghost_image(_ax, points, _levels, _min_flux, _max_flux, _power_scale):
    # ghost image
    points_inner = points.iloc[[b_ < self.get_apparent_inner_edge_radius(a_ + np.pi) for b_, a_ in
                                zip(points["impact_parameter"], points["angle"])]]
    points_outer = points.iloc[[b_ > self.get_apparent_outer_edge_radius(a_ + np.pi) for b_, a_ in
                                zip(points["impact_parameter"], points["angle"])]]
    
    for i, points_ in enumerate([points_inner, points_outer]):
        points_.sort_values(by=['flux_o'], ascending=False)
        fluxes = [(abs(fl + _min_flux) / (_max_flux + _min_flux)) ** _power_scale for fl in
                  points_['flux_o']]
        _ax.tricontourf(points_['X'], [-e for e in points_['Y']], fluxes, cmap='Greys_r',
                        norm=plt.Normalize(0, 1), levels=_levels, nchunk=2, zorder=1 - i)
                """,
                "critical_features": [
                    "Y-coordinate flipping: [-e for e in points_['Y']]",
                    "Angle offset: a_ + np.pi for edge calculations",
                    "Inner/outer region splitting",
                    "Specific zorder for layering"
                ]
            },
            
            "direct_image_rendering": {
                "file": "references/luminet/core/black_hole.py",
                "location": "plot_direct_image function in plot_points method",
                "code": """
def plot_direct_image(_ax, points, _levels, _min_flux, _max_flux, _power_scale):
    # direct image
    points.sort_values(by="angle", inplace=True)
    points_ = points.iloc[[b_ <= self.get_apparent_outer_edge_radius(a_) for b_, a_ in
                           zip(points["impact_parameter"], points["angle"])]]
    fluxes = [(abs(fl + _min_flux) / (_max_flux + _min_flux)) ** _power_scale for fl in points_['flux_o']]
    _ax.tricontourf(points_['X'], points_['Y'], fluxes, cmap='Greys_r',
                    levels=_levels, norm=plt.Normalize(0, 1), nchunk=2)
                """,
                "critical_features": [
                    "No Y-coordinate flipping for direct image",
                    "Filtering by apparent outer edge",
                    "Same flux normalization formula"
                ]
            },
            
            "artifact_masking": {
                "file": "references/luminet/core/black_hole.py",
                "location": "plot_points method",
                "code": """
br = self.calc_apparent_inner_disk_edge()
_ax.fill_between(br.X, br.Y, color='black', zorder=1)  # fill Delauney triangulation artefacts

x, y = self.apparent_inner_edge(cartesian=True)
_ax.fill_between(x, y, color='black', zorder=1)  # fill Delauney triangulation artefacts

x, y = self.calc_apparent_outer_disk_edge().cartesian_co
_ax.fill_between(x, y, color='black', zorder=0)  # fill Delauney triangulation artefacts
                """,
                "significance": "Black fill_between to mask triangulation artifacts"
            }
        }
        
        return patterns
        
    def extract_physics_code(self) -> Dict:
        """Extract the exact physics calculation code."""
        
        patterns = {
            "impact_parameter_calculation": {
                "file": "references/luminet/core/bh_math.py",
                "location": "calc_impact_parameter function",
                "code": """
def calc_impact_parameter(_r, incl, _alpha, bh_mass, midpoint_iterations=100, plot_inbetween=False,
                          n=0, min_periastron=1., initial_guesses=20, use_ellipse=True) -> float:
    periastron_solution = calc_periastron(_r, incl, _alpha, bh_mass, midpoint_iterations, plot_inbetween, n,
                                          min_periastron, initial_guesses)
    if periastron_solution is None or periastron_solution <= 2.*bh_mass:
        return ellipse(_r, _alpha, incl)
    elif periastron_solution > 2.*bh_mass:
        b = calc_b_from_periastron(periastron_solution, bh_mass)
        return b
                """,
                "key_points": [
                    "n=0 for direct image, n=1 for ghost image",
                    "Fallback to ellipse() for non-physical solutions",
                    "Midpoint refinement for precision"
                ]
            },
            
            "redshift_factor_calculation": {
                "file": "references/luminet/core/bh_math.py",
                "location": "redshift_factor function",
                "code": """
def redshift_factor(radius, angle, incl, bh_mass, b_):
    z_factor = (1. + np.sqrt(bh_mass / (radius ** 3)) * b_ * np.sin(incl) * np.sin(angle)) * \\
               (1 - 3. * bh_mass / radius) ** -.5
    return z_factor
                """,
                "significance": "Combined gravitational and Doppler redshift"
            },
            
            "flux_calculation": {
                "file": "references/luminet/core/bh_math.py",
                "location": "flux_observed function",
                "code": """
def flux_observed(r, acc, bh_mass, redshift_factor):
    flux_intr = flux_intrinsic(r, acc, bh_mass)
    return flux_intr / redshift_factor ** 4
                """,
                "significance": "Fourth power redshift correction"
            }
        }
        
        return patterns
        
    def generate_code_documentation(self) -> str:
        """Generate comprehensive code documentation."""
        
        doc = """# Luminet Reference Implementation Code Patterns

This document contains the exact code patterns extracted from the reference
Luminet implementation, organized by functional area.

## 1. Coordinate Transformation Patterns

"""
        
        coord_patterns = self.extract_coordinate_transformation_code()
        for pattern_name, details in coord_patterns.items():
            doc += f"### {pattern_name.replace('_', ' ').title()}\n\n"
            doc += f"**File**: {details['file']}\n\n"
            doc += f"**Code**:\n```python{details['code']}\n```\n\n"
            if 'significance' in details:
                doc += f"**Significance**: {details['significance']}\n\n"
                
        doc += "## 2. Sampling Methodology Patterns\n\n"
        
        sampling_patterns = self.extract_sampling_code()
        for pattern_name, details in sampling_patterns.items():
            doc += f"### {pattern_name.replace('_', ' ').title()}\n\n"
            doc += f"**File**: {details['file']}\n\n"
            doc += f"**Code**:\n```python{details['code']}\n```\n\n"
            if 'key_points' in details:
                doc += "**Key Points**:\n"
                for point in details['key_points']:
                    doc += f"- {point}\n"
                doc += "\n"
                
        doc += "## 3. Visualization Rendering Patterns\n\n"
        
        viz_patterns = self.extract_visualization_code()
        for pattern_name, details in viz_patterns.items():
            doc += f"### {pattern_name.replace('_', ' ').title()}\n\n"
            doc += f"**File**: {details['file']}\n\n"
            doc += f"**Code**:\n```python{details['code']}\n```\n\n"
            if 'critical_features' in details:
                doc += "**Critical Features**:\n"
                for feature in details['critical_features']:
                    doc += f"- {feature}\n"
                doc += "\n"
                
        doc += "## 4. Physics Calculation Patterns\n\n"
        
        physics_patterns = self.extract_physics_code()
        for pattern_name, details in physics_patterns.items():
            doc += f"### {pattern_name.replace('_', ' ').title()}\n\n"
            doc += f"**File**: {details['file']}\n\n"
            doc += f"**Code**:\n```python{details['code']}\n```\n\n"
            if 'key_points' in details:
                doc += "**Key Points**:\n"
                for point in details['key_points']:
                    doc += f"- {point}\n"
                doc += "\n"
                
        return doc
        
    def save_code_documentation(self):
        """Save the code documentation to file."""
        doc = self.generate_code_documentation()
        
        if not os.path.exists("analysis_output"):
            os.makedirs("analysis_output")
            
        with open("analysis_output/luminet_code_patterns.md", 'w') as f:
            f.write(doc)
            
        print("Code patterns documentation saved to analysis_output/luminet_code_patterns.md")

def main():
    """Main execution function."""
    extractor = LuminetCodeExtractor()
    extractor.save_code_documentation()

if __name__ == "__main__":
    main()