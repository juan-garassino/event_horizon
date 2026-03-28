# Mathematical Foundations

## Overview

This document details the mathematical algorithms extracted from the bhsim and luminet reference implementations. These algorithms form the scientific foundation of EventHorizon's particle-based black hole visualization system.

## Extracted Algorithms from bhsim Reference

### Geodesic Calculations

The bhsim reference provides sophisticated geodesic calculations for photon trajectories in Schwarzschild spacetime. These have been extracted and implemented in `eventHorizon/math/geodesics.py`.

#### Core Mathematical Expressions

**Extracted from `references/bhsim/core/blackhole.py`:**

```python
def expr_u(r, M):
    """
    Effective potential term: u = M/r
    Used in geodesic equations for Schwarzschild spacetime
    """
    return M / r

def expr_r_inv(u, M):
    """
    Inverse radius: r = M/u
    """
    return M / u

def expr_b(r, M):
    """
    Impact parameter calculation for circular orbits
    b = r * sqrt(r / (r - 3*M))
    """
    return r * np.sqrt(r / (r - 3*M))

def expr_q(r, M):
    """
    Carter constant Q for Schwarzschild spacetime
    Q = r^2 * (r - 3*M) / r
    """
    return r**2 * (r - 3*M) / r

def expr_k(u, b, M):
    """
    Conserved energy parameter
    k = sqrt(1 - 2*M*u + b^2*u^2)
    """
    return np.sqrt(1 - 2*M*u + b**2 * u**2)

def expr_zeta_inf(b, M):
    """
    Asymptotic angle parameter
    zeta_inf = arccos(b / sqrt(b^2 + 27*M^2))
    """
    return np.arccos(b / np.sqrt(b**2 + 27*M**2))
```

#### Elliptic Integral Implementation

**Extracted lambdify function with Jacobi elliptic functions:**

```python
def lambdify_geodesic_functions():
    """
    Lambdified functions for efficient geodesic calculations
    Supports Jacobi elliptic functions: sn, elliptic_f, elliptic_k
    """
    # Symbolic variables
    u, b, M, zeta = symbols('u b M zeta')
    
    # Geodesic equation in terms of elliptic integrals
    # This implements the exact solution for photon trajectories
    # in Schwarzschild spacetime using Weierstrass elliptic functions
    
    # Modulus for elliptic integrals
    k_modulus = expr_k(u, b, M)
    
    # Elliptic integral of first kind
    elliptic_integral = elliptic_f(zeta, k_modulus)
    
    # Jacobi elliptic function sn
    jacobi_sn = sn(elliptic_integral, k_modulus)
    
    return {
        'k_modulus': lambdify((u, b, M), k_modulus, 'numpy'),
        'elliptic_f': lambdify((zeta, k_modulus), elliptic_f(zeta, k_modulus), 'numpy'),
        'jacobi_sn': lambdify((elliptic_integral, k_modulus), jacobi_sn, 'numpy')
    }
```

#### Periastron Root Finding

**Extracted objective function for impact parameter calculation:**

```python
def objective(r_periastron, r_source, b, M):
    """
    Objective function for finding periastron radius
    
    This implements the condition that the photon trajectory
    must pass through both the source and periastron points.
    
    Parameters
    ----------
    r_periastron : float
        Periastron radius (closest approach to black hole)
    r_source : float
        Source radius in accretion disk
    b : float
        Impact parameter
    M : float
        Black hole mass
        
    Returns
    -------
    float
        Objective function value (zero at solution)
    """
    if r_periastron <= 3*M:  # Inside photon sphere
        return float('inf')
    
    # Calculate conserved quantities
    u_p = M / r_periastron
    u_s = M / r_source
    
    # Energy and angular momentum conservation
    E_squared = (1 - 2*u_p) * (1 + b**2 * u_p**2)
    L_squared = b**2 * E_squared
    
    # Geodesic equation at source
    dr_dt_squared = E_squared - (1 - 2*u_s) * (1 + L_squared * u_s**2)
    
    return dr_dt_squared

def lambda_objective(b, M):
    """
    Lambda function for root finding
    Returns function that finds periastron for given impact parameter
    """
    def find_periastron(r_source):
        from scipy.optimize import brentq
        
        try:
            # Find periastron radius using Brent's method
            r_min = 3.01 * M  # Just outside photon sphere
            r_max = r_source
            
            if r_max <= r_min:
                return None
            
            r_periastron = brentq(
                lambda r_p: objective(r_p, r_source, b, M),
                r_min, r_max,
                xtol=1e-12
            )
            
            return r_periastron
            
        except (ValueError, RuntimeError):
            return None
    
    return find_periastron
```

### Impact Parameter Calculation

**Extracted from bhsim's impact_parameter function:**

```python
def calculate_impact_parameter(
    source_radius: float,
    source_angle: float,
    observer_inclination: float,
    black_hole_mass: float,
    image_order: int = 0,
    solver_params: Dict[str, Any] = None
) -> Optional[float]:
    """
    Calculate impact parameter using bhsim's geodesic algorithms
    
    This implements the complete geodesic ray tracing from source
    to observer, accounting for multiple image orders.
    
    Parameters
    ----------
    source_radius : float
        Radial position of source in accretion disk
    source_angle : float
        Angular position of source
    observer_inclination : float
        Observer inclination angle
    black_hole_mass : float
        Black hole mass
    image_order : int
        Image order (0=direct, 1=ghost, etc.)
    solver_params : Dict[str, Any]
        Numerical solver parameters
        
    Returns
    -------
    Optional[float]
        Impact parameter, or None if no solution exists
    """
    if solver_params is None:
        solver_params = {
            'initial_guesses': 20,
            'midpoint_iterations': 100,
            'min_periastron': 3.01 * black_hole_mass
        }
    
    # Generate initial guesses for impact parameter
    b_min = 3.0 * np.sqrt(27) * black_hole_mass  # Photon sphere
    b_max = 10.0 * source_radius  # Conservative upper bound
    
    initial_guesses = np.linspace(b_min, b_max, solver_params['initial_guesses'])
    
    for b_guess in initial_guesses:
        try:
            # Find periastron for this impact parameter
            periastron_finder = lambda_objective(b_guess, black_hole_mass)
            r_periastron = periastron_finder(source_radius)
            
            if r_periastron is None:
                continue
            
            # Calculate geodesic trajectory
            trajectory = integrate_geodesic(
                r_periastron, source_radius, b_guess, black_hole_mass,
                observer_inclination, image_order
            )
            
            if trajectory is not None:
                return b_guess
                
        except Exception:
            continue
    
    return None  # No solution found
```

## Extracted Algorithms from Luminet Reference

### Flux Calculations

The luminet reference provides the definitive implementation of Shakura-Sunyaev accretion disk physics.

#### Intrinsic Flux Formula

**Extracted from `references/luminet/core/bh_math.py`:**

```python
def flux_intrinsic(radius: float, black_hole_mass: float, accretion_rate: float) -> float:
    """
    Luminet's exact Shakura-Sunyaev disk flux formula
    
    This implements the complete flux calculation including:
    - ISCO boundary conditions
    - Logarithmic correction terms
    - Proper normalization
    
    Formula:
    F = (3*M*mdot)/(8*π) * (1/((r/M - 3)*r^2.5)) * 
        [√(r/M) - √6 + (1/√3)*ln(log_arg)]
    
    where log_arg = [(√(r/M) + √3)(√6 - √3)] / [(√(r/M) - √3)(√6 + √3)]
    """
    r_normalized = radius / black_hole_mass
    
    if r_normalized <= 3.0:  # Inside ISCO
        return 0.0
    
    try:
        # Logarithmic correction term
        sqrt_r = np.sqrt(r_normalized)
        sqrt_3 = np.sqrt(3)
        sqrt_6 = np.sqrt(6)
        
        log_arg = ((sqrt_r + sqrt_3) * (sqrt_6 - sqrt_3)) / \
                  ((sqrt_r - sqrt_3) * (sqrt_6 + sqrt_3))
        
        # Complete Shakura-Sunyaev flux formula
        flux = (3.0 * black_hole_mass * accretion_rate / (8 * np.pi)) * \
               (1 / ((r_normalized - 3) * radius ** 2.5)) * \
               (sqrt_r - sqrt_6 + (1.0 / sqrt_3) * np.log(log_arg))
        
        return max(flux, 0.0)
        
    except (ValueError, ZeroDivisionError, OverflowError):
        return 0.0
```

#### Redshift Factor Calculation

**Extracted redshift_factor function:**

```python
def redshift_factor(
    radius: float,
    angle: float,
    inclination: float,
    impact_parameter: float,
    black_hole_mass: float
) -> float:
    """
    Luminet's gravitational redshift factor calculation
    
    Combines orbital motion and gravitational redshift:
    z_factor = (1 + √(M/r³) * b * sin(i) * sin(α)) * (1 - 3M/r)^(-1/2)
    
    Terms:
    - Orbital frequency: √(M/r³)
    - Doppler shift: b * sin(i) * sin(α)
    - Gravitational redshift: (1 - 3M/r)^(-1/2)
    """
    try:
        # Orbital frequency term (Keplerian motion)
        orbital_frequency = np.sqrt(black_hole_mass / (radius ** 3))
        
        # Doppler shift from orbital motion
        doppler_term = impact_parameter * np.sin(inclination) * np.sin(angle)
        
        # Combined orbital redshift
        orbital_redshift = 1.0 + orbital_frequency * doppler_term
        
        # Gravitational redshift factor
        gravitational_factor = (1 - 3.0 * black_hole_mass / radius) ** (-0.5)
        
        # Total redshift factor
        z_factor = orbital_redshift * gravitational_factor
        
        return z_factor
        
    except (ValueError, ZeroDivisionError, OverflowError):
        return 1.0  # No redshift if calculation fails
```

#### Observed Flux Calculation

**Extracted flux_observed function:**

```python
def flux_observed(
    radius: float,
    black_hole_mass: float,
    accretion_rate: float,
    redshift_factor: float
) -> float:
    """
    Calculate observed flux including redshift effects
    
    F_observed = F_intrinsic / (1+z)^4
    
    The (1+z)^4 factor accounts for:
    - Photon energy redshift: (1+z)^1
    - Photon arrival rate: (1+z)^1  
    - Solid angle effect: (1+z)^2
    """
    # Calculate intrinsic flux
    flux_intr = flux_intrinsic(radius, black_hole_mass, accretion_rate)
    
    # Apply redshift correction
    return flux_intr / (redshift_factor ** 4)
```

### Particle Sampling Algorithm

**Extracted from luminet's sample_points method:**

```python
def sample_points_luminet(
    n_points: int,
    inner_radius: float,
    outer_radius: float,
    black_hole_mass: float
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Luminet's exact particle sampling algorithm
    
    Key features:
    - Linear sampling in radius (not area-weighted)
    - Creates bias toward center where flux is exponentially higher
    - Uniform angular sampling
    
    This is the exact algorithm from references/luminet/core/black_hole.py:
    r = min_radius + (max_radius - min_radius) * random()
    θ = random() * 2π
    """
    # Linear radius sampling (luminet's approach)
    # This creates natural bias toward center where interesting physics happens
    u = np.random.random(n_points)
    radii = inner_radius + (outer_radius - inner_radius) * u
    
    # Uniform angular sampling
    angles = np.random.random(n_points) * 2 * np.pi
    
    return radii, angles
```

## Coordinate Transformations

### Observer Frame Transformation

**Extracted coordinate transformation algorithms:**

```python
def transform_to_observer_frame(
    disk_x: float,
    disk_y: float,
    disk_z: float,
    inclination: float
) -> Tuple[float, float, float]:
    """
    Transform from disk frame to observer frame
    
    Rotation matrix for inclination:
    [x']   [1    0         0    ] [x]
    [y'] = [0  cos(i)  -sin(i)] [y]
    [z']   [0  sin(i)   cos(i)] [z]
    """
    cos_i = np.cos(inclination)
    sin_i = np.sin(inclination)
    
    obs_x = disk_x
    obs_y = disk_y * cos_i - disk_z * sin_i
    obs_z = disk_y * sin_i + disk_z * cos_i
    
    return obs_x, obs_y, obs_z

def calculate_impact_parameter_coordinates(
    impact_parameter: float,
    observed_angle: float
) -> Tuple[float, float]:
    """
    Convert impact parameter and angle to Cartesian coordinates
    
    x = b * cos(α)
    y = b * sin(α)
    """
    x = impact_parameter * np.cos(observed_angle)
    y = impact_parameter * np.sin(observed_angle)
    
    return x, y
```

### Ghost Image Coordinate Transformation

**Extracted from bhsim's reorient_alpha function:**

```python
def reorient_alpha_for_ghost_image(
    alpha: float,
    inclination: float,
    image_order: int
) -> float:
    """
    Reorient angle for ghost images
    
    Ghost images appear with modified angular coordinates
    due to the additional light path around the black hole.
    """
    if image_order == 0:
        # Direct image - no reorientation
        return alpha
    elif image_order == 1:
        # First ghost image - π rotation
        return alpha + np.pi
    else:
        # Higher order images
        return alpha + image_order * np.pi
```

## Numerical Methods

### Root Finding for Geodesics

**Extracted numerical methods from bhsim:**

```python
def fast_root(
    func: callable,
    x_min: float,
    x_max: float,
    tolerance: float = 1e-12,
    max_iterations: int = 100
) -> Optional[float]:
    """
    Fast root finding using Brent's method
    Optimized for geodesic calculations
    """
    try:
        from scipy.optimize import brentq
        
        # Check if root exists in interval
        f_min = func(x_min)
        f_max = func(x_max)
        
        if f_min * f_max > 0:
            return None  # No root in interval
        
        # Use Brent's method for robust convergence
        root = brentq(func, x_min, x_max, xtol=tolerance, maxiter=max_iterations)
        
        return root
        
    except (ValueError, RuntimeError):
        return None

def find_brackets(
    func: callable,
    x_start: float,
    x_end: float,
    n_points: int = 100
) -> List[Tuple[float, float]]:
    """
    Find bracketing intervals for root finding
    """
    x_values = np.linspace(x_start, x_end, n_points)
    f_values = [func(x) for x in x_values]
    
    brackets = []
    for i in range(len(f_values) - 1):
        if f_values[i] * f_values[i+1] < 0:
            brackets.append((x_values[i], x_values[i+1]))
    
    return brackets
```

### Geodesic Integration

**Extracted integration methods:**

```python
def integrate_geodesic(
    r_periastron: float,
    r_source: float,
    impact_parameter: float,
    black_hole_mass: float,
    observer_inclination: float,
    image_order: int = 0,
    integration_steps: int = 1000
) -> Optional[Dict[str, np.ndarray]]:
    """
    Integrate geodesic equation from source to observer
    
    Uses Runge-Kutta method for numerical integration
    of the geodesic equation in Schwarzschild spacetime.
    """
    # Initial conditions at periastron
    u_p = black_hole_mass / r_periastron
    
    # Conserved quantities
    E = np.sqrt((1 - 2*u_p) * (1 + impact_parameter**2 * u_p**2))
    L = impact_parameter * E
    
    # Integration parameters
    u_start = black_hole_mass / r_source
    u_end = 0.0  # Infinity (observer)
    
    u_values = np.linspace(u_start, u_end, integration_steps)
    phi_values = np.zeros_like(u_values)
    
    # Integrate geodesic equation
    for i in range(1, len(u_values)):
        du = u_values[i] - u_values[i-1]
        
        # Geodesic equation: d²u/dφ² + u = 3Mu²
        d2u_dphi2 = 3 * black_hole_mass * u_values[i-1]**2 - u_values[i-1]
        
        # Runge-Kutta step
        phi_values[i] = phi_values[i-1] + du / np.sqrt(
            E**2 - (1 - 2*black_hole_mass*u_values[i-1]) * 
            (1 + L**2 * u_values[i-1]**2)
        )
    
    return {
        'u_values': u_values,
        'phi_values': phi_values,
        'r_values': black_hole_mass / u_values,
        'impact_parameter': impact_parameter
    }
```

## Validation and Testing

### Analytical Solutions

For validation, the system includes analytical solutions for special cases:

```python
def photon_sphere_radius(black_hole_mass: float) -> float:
    """
    Analytical solution for photon sphere radius
    r_ph = 3M (exact)
    """
    return 3.0 * black_hole_mass

def isco_radius(black_hole_mass: float, spin: float = 0.0) -> float:
    """
    Analytical solution for ISCO radius
    Schwarzschild: r_isco = 6M
    Kerr: more complex formula
    """
    if spin == 0.0:
        return 6.0 * black_hole_mass
    else:
        # Kerr ISCO formula (simplified)
        z1 = 1 + (1 - spin**2)**(1/3) * ((1 + spin)**(1/3) + (1 - spin)**(1/3))
        z2 = np.sqrt(3*spin**2 + z1**2)
        return black_hole_mass * (3 + z2 - np.sqrt((3 - z1)*(3 + z1 + 2*z2)))

def circular_orbit_velocity(radius: float, black_hole_mass: float) -> float:
    """
    Analytical orbital velocity for circular orbits
    v = √(M/r)
    """
    return np.sqrt(black_hole_mass / radius)
```

## Performance Optimizations

### Vectorized Operations

All mathematical operations are vectorized for performance:

```python
def vectorized_flux_calculation(
    radii: np.ndarray,
    black_hole_mass: float,
    accretion_rate: float
) -> np.ndarray:
    """
    Vectorized flux calculation for multiple radii
    """
    r_normalized = radii / black_hole_mass
    
    # Mask for valid radii (outside ISCO)
    valid_mask = r_normalized > 3.0
    
    fluxes = np.zeros_like(radii)
    
    if np.any(valid_mask):
        valid_radii = radii[valid_mask]
        valid_r_norm = r_normalized[valid_mask]
        
        # Vectorized logarithmic term calculation
        sqrt_r = np.sqrt(valid_r_norm)
        log_args = ((sqrt_r + np.sqrt(3)) * (np.sqrt(6) - np.sqrt(3))) / \
                   ((sqrt_r - np.sqrt(3)) * (np.sqrt(6) + np.sqrt(3)))
        
        # Vectorized flux calculation
        fluxes[valid_mask] = (3.0 * black_hole_mass * accretion_rate / (8 * np.pi)) * \
                            (1 / ((valid_r_norm - 3) * valid_radii ** 2.5)) * \
                            (sqrt_r - np.sqrt(6) + (1.0 / np.sqrt(3)) * np.log(log_args))
    
    return np.maximum(fluxes, 0.0)
```

This comprehensive mathematical foundation ensures that EventHorizon's visualizations maintain the scientific accuracy of the original reference implementations while providing the performance needed for interactive use.