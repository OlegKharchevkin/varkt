import math
import time
import krpc


def auto(dv, dfi, V_mun, R_mun, mu):
    turn_start_altitude = 500
    turn_end_altitude = 90000
    target_altitude = 300000

    conn = krpc.connect(name='Launch into orbit')
    vessel = conn.space_center.active_vessel

    # Set up streams for telemetry
    ut = conn.add_stream(getattr, conn.space_center, 'ut')
    altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
    apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
    stage_2_resources = vessel.resources_in_decouple_stage(
        stage=1, cumulative=False)
    srb_fuel = conn.add_stream(stage_2_resources.amount, 'SolidFuel')
    # Pre-launch setup
    """
    vessel.control.sas = False
    vessel.control.rcs = False
    vessel.control.throttle = 1.0

    # Countdown...
    print('3...')
    time.sleep(1)
    print('2...')
    time.sleep(1)
    print('1...')
    time.sleep(1)
    print('Launch!')
    # Activate the first stage
    """
    vessel.control.activate_next_stage()
    vessel.auto_pilot.engage()
    """
    vessel.auto_pilot.target_pitch_and_heading(90, 90)
    # Main ascent loop
    srbs_separated = False
    turn_angle = 0
    while True:

        # Gravity turn
        if altitude() > turn_start_altitude and altitude() < turn_end_altitude:
            frac = ((altitude() - turn_start_altitude) /
                    (turn_end_altitude - turn_start_altitude))
            new_turn_angle = frac * 90
            if abs(new_turn_angle - turn_angle) > 0.5:
                turn_angle = new_turn_angle
                vessel.auto_pilot.target_pitch_and_heading(90-turn_angle, 90)

        # Separate SRBs when finished
        if not srbs_separated:
            if srb_fuel() < 0.1:
                vessel.control.activate_next_stage()
                srbs_separated = True
                print('SRBs separated')

        # Decrease throttle when approaching target apoapsis
        if apoapsis() > target_altitude*0.9:
            print('Approaching target apoapsis')
            break

    # Disable engines when target apoapsis is reached
    vessel.control.throttle = 0.25
    while apoapsis() < target_altitude:
        pass
    print('Target apoapsis reached')
    vessel.control.throttle = 0.0

    # Wait until out of atmosphere
    print('Coasting out of atmosphere')
    while altitude() < 70500:
        pass
    # Plan circularization burn (using vis-viva equation)
    print('Planning circularization burn')
    mu = vessel.orbit.body.gravitational_parameter
    r = vessel.orbit.apoapsis
    a1 = vessel.orbit.semi_major_axis
    a2 = r
    v1 = math.sqrt(mu*((2./r)-(1./a1)))
    v2 = math.sqrt(mu*((2./r)-(1./a2)))
    delta_v = v2 - v1
    node = vessel.control.add_node(
        ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

    # Calculate burn time (using rocket equation)
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.82
    m0 = vessel.mass
    m1 = m0 / math.exp(delta_v/Isp)
    flow_rate = F / Isp
    burn_time = (m0 - m1) / flow_rate
    # Orientate ship
    print('Orientating ship for circularization burn')
    vessel.auto_pilot.reference_frame = node.reference_frame
    vessel.auto_pilot.target_direction = (0, 1, 0)
    vessel.auto_pilot.wait()

    # Wait until burn
    print('Waiting until circularization burn')
    burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time/2.)
    lead_time = 5
    conn.space_center.warp_to(burn_ut - lead_time)
    # Execute burn
    print('Ready to execute burn')
    time_to_apoapsis = conn.add_stream(
        getattr, vessel.orbit, 'time_to_apoapsis')
    while time_to_apoapsis() - (burn_time/2.) > 0:
        pass
    print('Executing burn')
    vessel.control.throttle = 1.0
    time.sleep(burn_time - 1)
    print('Fine tuning')
    vessel.control.throttle = 0.2
    remaining_burn = conn.add_stream(
        node.remaining_burn_vector, node.reference_frame)
    while remaining_burn()[1] > 0.4:
        pass
    vessel.control.throttle = 0.0
    node.remove()
    vessel.control.activate_next_stage()
    print('Launch complete')
    """
    bodyRadius = conn.space_center.bodies["Mun"].orbit.radius
    vesselRadius = vessel.orbit.radius
    bodyPos = conn.space_center.bodies["Mun"].orbit.position_at(
        ut(), conn.space_center.bodies["Mun"].reference_frame)
    vesselPos = vessel.orbit.position_at(
        ut(), conn.space_center.bodies["Mun"].reference_frame)
    distance = math.sqrt((bodyPos[0] - vesselPos[0])**2 +
                         (bodyPos[1] - vesselPos[1])**2 +
                         (bodyPos[2] - vesselPos[2])**2)
    fi = math.acos((bodyRadius**2 + vesselRadius**2 - distance **
                   2) / (2 * bodyRadius * vesselRadius))
    print(fi)
    w_mun = V_mun/R_mun
    v_ves = math.sqrt((vessel.velocity(conn.space_center.bodies["Mun"].reference_frame)[0])**2 +
                      (vessel.velocity(conn.space_center.bodies["Mun"].reference_frame)[1])**2 +
                      (vessel.velocity(conn.space_center.bodies["Mun"].reference_frame)[2])**2) + w_mun * vesselRadius
    w_ves = v_ves/vesselRadius
    bodyRadius = conn.space_center.bodies["Mun"].orbit.radius
    vesselRadius = vessel.orbit.radius
    bodyPos = conn.space_center.bodies["Mun"].orbit.position_at(
        ut(), conn.space_center.bodies["Mun"].reference_frame)
    vesselPos = vessel.orbit.position_at(
        ut(), conn.space_center.bodies["Mun"].reference_frame)
    distance = math.sqrt((bodyPos[0] - vesselPos[0])**2 +
                         (bodyPos[1] - vesselPos[1])**2 +
                         (bodyPos[2] - vesselPos[2])**2)
    nfi = math.acos((bodyRadius**2 + vesselRadius**2 - distance **
                     2) / (2 * bodyRadius * vesselRadius))
    if nfi < fi:
        dfi = (- dfi + nfi) % (2 * math.pi)
    else:
        dfi = (- dfi - nfi) % (2 * math.pi)
    dt = ut() + dfi / (w_ves-w_mun)
    lead_time = 20

    conn.space_center.warp_to(dt - lead_time)
    node = vessel.control.add_node(dt)
    v_ves = math.sqrt((vessel.velocity(conn.space_center.bodies["Mun"].reference_frame)[0])**2 +
                      (vessel.velocity(conn.space_center.bodies["Mun"].reference_frame)[1])**2 +
                      (vessel.velocity(conn.space_center.bodies["Mun"].reference_frame)[2])**2) + w_mun * vesselRadius

    node.prograde = dv - v_ves
    vessel.auto_pilot.reference_frame = node.reference_frame
    vessel.auto_pilot.target_direction = (0, 1, 0)
    vessel.auto_pilot.wait()
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.82
    m0 = vessel.mass
    m1 = m0 / math.exp((dv - v_ves)/Isp)
    flow_rate = F / Isp
    burn_time = (m0 - m1) / flow_rate

    while dt - ut() - (burn_time/2) > 0:
        pass
    vessel.control.throttle = 1.0
    time.sleep(burn_time - 1)
    vessel.control.throttle = 0.2
    remaining_burn = conn.add_stream(
        node.remaining_burn_vector, node.reference_frame)
    while remaining_burn()[1] > 0.4:
        pass
    vessel.control.throttle = 0.0
    node.remove()
    print(dt, w_ves-w_mun)
    dt = ut() + vessel.orbit.time_to_soi_change()
    conn.space_center.warp_to(dt + 1)
    mu = vessel.orbit.body.gravitational_parameter
    r = vessel.orbit.periapsis_altitude
    a1 = vessel.orbit.semi_major_axis
    a2 = r
    v1 = math.sqrt(mu*((2./r)-(1./a1)))
    v2 = math.sqrt(mu*((2./r)-(1./a2)))
    delta_v = v2 - v1
    node = vessel.control.add_node(
        ut() + vessel.orbit.time_to_periapsis, prograde=delta_v)

    # Calculate burn time (using rocket equation)
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.82
    m0 = vessel.mass
    m1 = m0 / math.exp(delta_v/Isp)
    flow_rate = F / Isp
    burn_time = (m0 - m1) / flow_rate
    # Orientate ship
    print('Orientating ship for circularization burn')
    vessel.auto_pilot.reference_frame = node.reference_frame
    vessel.auto_pilot.target_direction = (0, 1, 0)
    vessel.auto_pilot.wait()

    # Wait until burn
    print('Waiting until circularization burn')
    burn_ut = ut() + vessel.orbit.time_to_periapsis - (burn_time/2.)
    lead_time = 5
    conn.space_center.warp_to(burn_ut - lead_time)
    # Execute burn
    print('Ready to execute burn')
    time_to_periapsis = conn.add_stream(
        getattr, vessel.orbit, 'time_to_periapsis')
    while time_to_periapsis() - (burn_time/2.) > 0:
        pass
    print('Executing burn')
    vessel.control.throttle = 1.0
    time.sleep(burn_time - 1)
    print('Fine tuning')
    vessel.control.throttle = 0.2
    remaining_burn = conn.add_stream(
        node.remaining_burn_vector, node.reference_frame)
    while remaining_burn()[1] > 0.4:
        pass
    vessel.control.throttle = 0.0
    node.remove()


if __name__ == "__main__":
    auto(2705, 1.849957894568604)
