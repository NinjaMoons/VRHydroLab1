#!/usr/bin/env python3

"""Analytical section parameters for the LR6 conical Laval nozzle."""

import argparse
import json
import math


def section(beta, p0, t0, mass_flow, gas_r, gamma):
    pressure = beta * p0
    temperature = t0 * beta ** ((gamma - 1.0) / gamma)
    specific_volume = gas_r * temperature / pressure
    density = 1.0 / specific_volume
    velocity = math.sqrt(2.0 * gamma / (gamma - 1.0) * gas_r * (t0 - temperature))
    sound_speed = math.sqrt(gamma * gas_r * temperature)
    area = mass_flow / (density * velocity)
    diameter = math.sqrt(4.0 * area / math.pi)
    return {
        "beta": beta,
        "p_Pa": pressure,
        "T_K": temperature,
        "rho_kg_m3": density,
        "U_m_s": velocity,
        "a_m_s": sound_speed,
        "Mach": velocity / sound_speed,
        "area_m2": area,
        "diameter_m": diameter,
        "diameter_mm": diameter * 1000.0,
    }


def calculate(p0, t0, pout, mass_flow, alpha, beta_angle, gas_r=287.0, gamma=1.4):
    critical_beta = (2.0 / (gamma + 1.0)) ** (gamma / (gamma - 1.0))
    inlet = section(0.999, p0, t0, mass_flow, gas_r, gamma)
    throat = section(critical_beta, p0, t0, mass_flow, gas_r, gamma)
    outlet = section(pout / p0, p0, t0, mass_flow, gas_r, gamma)
    left = (inlet["diameter_m"] - throat["diameter_m"]) / (
        2.0 * math.tan(math.radians(alpha / 2.0))
    )
    right = (outlet["diameter_m"] - throat["diameter_m"]) / (
        2.0 * math.tan(math.radians(beta_angle / 2.0))
    )
    return {
        "inputs": {
            "p0_Pa": p0, "T0_K": t0, "pout_Pa": pout,
            "massFlow_kg_s": mass_flow, "alpha_deg": alpha,
            "beta_deg": beta_angle, "R_J_kgK": gas_r, "gamma": gamma,
        },
        "inlet": inlet,
        "throat": throat,
        "outlet": outlet,
        "geometry": {
            "length_convergent_m": left,
            "length_divergent_m": right,
            "rounding_radius_m": throat["diameter_m"],
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--p0", type=float, default=200000.0)
    parser.add_argument("--t0", type=float, default=1800.0)
    parser.add_argument("--pout", type=float, default=9000.0)
    parser.add_argument("--mass-flow", type=float, default=1.5)
    parser.add_argument("--alpha", type=float, default=14.0)
    parser.add_argument("--beta", type=float, default=28.0)
    args = parser.parse_args()
    print(json.dumps(calculate(args.p0, args.t0, args.pout, args.mass_flow,
                               args.alpha, args.beta), indent=2))
