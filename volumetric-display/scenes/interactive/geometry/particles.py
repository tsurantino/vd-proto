"""
Particle Flow Geometry Generators
Spiral/helix, galaxy, and explosion patterns
"""

import numpy as np


def generate_spiral(coords, grid_shape, params, time):
    """
    Spiral/helix pattern - travels along Z axis with adjustable parameters.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        params: SceneParameters object with size, density, amplitude, objectCount
        time: Animation time

    Returns:
        Boolean mask of spiral voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    center_x = width / 2
    center_y = height / 2
    center_z = length / 2

    # Size controls the overall radius of the helix
    radius = min(center_x, center_y) * params.size * 0.6

    # Density controls tightness of helix (rotations per unit length)
    # Higher density = more rotations = tighter spiral
    turns_per_length = 2 + params.density * 8  # 2-10 turns

    # Amplitude controls thickness of the helix tube
    tube_thickness = 1.5 + params.amplitude * 4  # 1.5-5.5 pixels

    # Number of separate helix strands (controlled by objectCount)
    num_strands = max(1, params.objectCount)

    mask = np.zeros(grid_shape, dtype=bool)

    for strand in range(num_strands):
        # Each strand has a phase offset
        phase_offset = (strand / num_strands) * 2 * np.pi

        # Create helix path along Z axis (depth/length)
        # For each Z position, calculate the expected X,Y based on helix equation
        z_normalized = (z_coords - center_z) / length  # -0.5 to 0.5

        # Helix angle based on length position and animation
        angle = z_normalized * turns_per_length * 2 * np.pi + time * 2 + phase_offset

        # Expected helix positions (spiraling in XY plane as we move along Z)
        helix_x = center_x + radius * np.cos(angle)
        helix_y = center_y + radius * np.sin(angle)

        # Distance from helix path
        dx = x_coords - helix_x
        dy = y_coords - helix_y
        distance = np.sqrt(dx**2 + dy**2)

        # Particles along the helix path
        mask |= distance < tube_thickness

    return mask


def generate_galaxy(coords, grid_shape, params, time):
    """
    Galaxy-style spiral arms - travels along Z axis with enhanced customization.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        params: SceneParameters object with size, density, amplitude, objectCount, frequency
        time: Animation time

    Returns:
        Boolean mask of galaxy voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    center_x = width / 2
    center_y = height / 2
    center_z = length / 2

    # Galaxy is in the XY plane (front-facing), extending along Z axis
    # Calculate cylindrical coordinates
    dx = x_coords - center_x
    dy = y_coords - center_y
    dz = z_coords - center_z

    radius_xy = np.sqrt(dx**2 + dy**2)
    angle = np.arctan2(dy, dx)

    # Size controls overall galaxy diameter (0.1-2.0 scale)
    galaxy_radius = min(center_x, center_y) * params.size * 0.9

    # Amplitude controls both disc thickness AND arm prominence
    # Lower amplitude = thin disc with subtle arms
    # Higher amplitude = thick disc with prominent arms
    base_disc_thickness = 1.5 + params.amplitude * 8  # 1.5-9.5 voxels

    # Density controls spiral tightness AND number of particles
    # Lower density = loose, open spiral
    # Higher density = tight, compressed spiral
    spiral_tightness = 1.0 + params.density * 4  # 1-5

    mask = np.zeros(grid_shape, dtype=bool)

    # Number of spiral arms (controlled by objectCount parameter)
    num_arms = max(2, min(6, params.objectCount))

    for arm in range(num_arms):
        arm_phase = (arm / num_arms) * 2 * np.pi

        # Logarithmic spiral: θ = a * ln(r)
        # Expected angle at this radius for this arm
        # Add time rotation for spinning galaxy
        expected_angle = spiral_tightness * np.log(radius_xy + 1) + arm_phase - time * 0.3

        # Angular distance from spiral arm (wrapping around)
        angle_diff = ((angle - expected_angle + np.pi) % (2 * np.pi)) - np.pi

        # Convert angular difference to linear distance at this radius
        arm_distance = np.abs(angle_diff * radius_xy)

        # Arm width varies with radius - thicker at center, thinner at edges
        # Also controlled by amplitude for more dramatic arms
        radius_factor = np.clip(radius_xy / (galaxy_radius + 0.1), 0, 1)
        arm_width = (2 + params.amplitude * 6) * (1.2 - radius_factor)

        # Distance from disc plane (Z axis) - variable thickness
        # Disc is thicker at center (bulge) and thinner at edges
        disc_thickness_at_radius = base_disc_thickness * (1.5 - radius_factor)
        disc_distance = np.abs(dz)

        # Add density variation along arms (more particles toward center)
        # This creates a more organic, cloud-like appearance
        density_factor = 1.0 - 0.3 * radius_factor

        # Combine conditions: near spiral arm AND near disc plane AND within galaxy radius
        in_arm = arm_distance < arm_width * density_factor
        in_disc = disc_distance < disc_thickness_at_radius
        in_galaxy = radius_xy < galaxy_radius

        mask |= (in_arm & in_disc & in_galaxy)

        # Add "dust lanes" - darker regions between arms
        # Create secondary, fainter structures
        if params.frequency > 2.0:  # Only add detail at higher frequency settings
            # Offset dust lane angle slightly
            dust_angle = expected_angle + np.pi / num_arms
            dust_angle_diff = ((angle - dust_angle + np.pi) % (2 * np.pi)) - np.pi
            dust_distance = np.abs(dust_angle_diff * radius_xy)

            # Narrower than main arms
            in_dust = dust_distance < arm_width * 0.4 * density_factor
            mask |= (in_dust & in_disc & in_galaxy)

    # Add central bulge (spheroidal)
    # Size controlled by size parameter
    bulge_radius = galaxy_radius * (0.15 + params.size * 0.1)
    # Bulge is slightly elongated along Z
    bulge_z_factor = 0.7  # Flatter bulge
    bulge_distance = np.sqrt(dx**2 + dy**2 + (dz * bulge_z_factor)**2)
    mask |= bulge_distance < bulge_radius

    # Add outer halo particles for visual interest (if amplitude is high)
    if params.amplitude > 0.5:
        halo_radius = galaxy_radius * 1.2
        halo_thickness = base_disc_thickness * 0.3

        # Sparse halo particles
        halo_condition = (
            (radius_xy > galaxy_radius * 0.9) &
            (radius_xy < halo_radius) &
            (disc_distance < halo_thickness) &
            # Make halo sparse using modulo pattern
            ((x_coords.astype(int) + y_coords.astype(int) + z_coords.astype(int)) % 3 == 0)
        )
        mask |= halo_condition

    return mask


def generate_explode(coords, grid_shape, params, time):
    """
    Particles exploding from a random center point.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        params: SceneParameters object with size, density, amplitude
        time: Animation time

    Returns:
        Boolean mask of explosion voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    # Use time to create explosion cycles
    # Each explosion lasts a few seconds, then resets
    explosion_cycle = 3.0  # seconds per explosion
    cycle_time = time % explosion_cycle

    # Generate a consistent random position for this cycle
    # Use floor division to get the cycle number
    cycle_num = int(time / explosion_cycle)

    # Pseudo-random center position based on cycle number
    np.random.seed(cycle_num * 42)
    center_x = np.random.randint(width // 4, 3 * width // 4)
    center_y = np.random.randint(height // 4, 3 * height // 4)
    center_z = np.random.randint(length // 4, 3 * length // 4)

    # Size controls the initial explosion size
    initial_radius = 2 + params.size * 3

    # Expansion over time - amplitude controls speed (5-15 units/sec for visible but not instant)
    # Reduced range to prevent particles from disappearing too quickly
    expansion_speed = 5 + params.amplitude * 10
    current_radius = initial_radius + expansion_speed * cycle_time

    # Shell thickness (ring of particles expanding)
    shell_thickness = 2 + params.size * 3

    # Calculate distance from explosion center
    dx = x_coords - center_x
    dy = y_coords - center_y
    dz = z_coords - center_z
    distance = np.sqrt(dx**2 + dy**2 + dz**2)

    # Density controls number of particles
    num_particles = int(50 + params.density * 200)

    # Create particle spray using polar coordinates
    mask = np.zeros(grid_shape, dtype=bool)

    np.random.seed(cycle_num * 42 + 1)  # Same seed for consistent directions

    for i in range(num_particles):
        # Random direction for each particle (spherical coordinates)
        theta = np.random.uniform(0, 2 * np.pi)
        phi = np.random.uniform(0, np.pi)

        # Particle position along its trajectory
        px = center_x + current_radius * np.sin(phi) * np.cos(theta)
        py = center_y + current_radius * np.sin(phi) * np.sin(theta)
        pz = center_z + current_radius * np.cos(phi)

        # Particle size (small)
        particle_size = 0.8 + params.size * 0.5

        # Distance to this particle
        pdx = x_coords - px
        pdy = y_coords - py
        pdz = z_coords - pz
        pdist = np.sqrt(pdx**2 + pdy**2 + pdz**2)

        mask |= pdist < particle_size

    return mask


def generate_flowing_particles(coords, grid_shape, params, time):
    """
    Default flowing particles pattern.

    Args:
        coords: Tuple of (z, y, x) coordinate arrays
        grid_shape: Tuple of (length, height, width)
        params: SceneParameters object with size, density
        time: Animation time

    Returns:
        Boolean mask of flowing particle voxels
    """
    z_coords, y_coords, x_coords = coords
    length, height, width = grid_shape

    mask = np.zeros(grid_shape, dtype=bool)
    num_particles = int(100 * params.density)

    for i in range(num_particles):
        seed = i * 12345
        px = ((seed % width) + time * 5 * (1 + i % 3)) % width
        py = ((seed * 7 % height) + time * 3 * (1 + i % 2)) % height
        pz = ((seed * 13 % length) + time * 4 * (1 + i % 4)) % length

        dx = x_coords - px
        dy = y_coords - py
        dz = z_coords - pz
        distance = np.sqrt(dx**2 + dy**2 + dz**2)

        particle_size = 2 * params.size
        mask |= distance < particle_size

    return mask
