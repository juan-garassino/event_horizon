from eventHorizon.core.ray_tracing import RayTracingEngine, RayTracingConfig
from eventHorizon.core.particle_system import Particle
from eventHorizon.core.particle_renderer import ParticleRenderer
import numpy as np

# 1️⃣ Create a circular distribution of particles in the disk
particles = [Particle(radius=10, angle=a, flux=1.0) for a in np.linspace(0, 2*np.pi, 200)]

# 2️⃣ Initialize ray tracing (this is the fixed engine)
engine = RayTracingEngine(RayTracingConfig(max_image_orders=2))

# 3️⃣ Compute direct and ghost rays → returns 2 pandas DataFrames
direct_df, ghost_df = engine.trace_particles_to_dataframes(particles, 80)

# 4️⃣ Render the two DataFrames into a Luminet-style image
renderer = ParticleRenderer()
fig, ax = renderer.render_frame(direct_df, ghost_df, viewport_config={'ax_lim': (-40, 40)})

# 5️⃣ Display the figure
fig.show()
