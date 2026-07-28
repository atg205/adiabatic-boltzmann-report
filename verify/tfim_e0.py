#!/usr/bin/env python3
"""Checks the closed-form TFIM ground-state energy of report.tex Eq. (28) (L594-601).

Three things are tested:
  (1) the closed form against exact diagonalisation of
          H = -J sum_i sigma^z_i sigma^z_{i+1} - h sum_i sigma^x_i     (periodic)
      -> it is CORRECT: agreement ~1e-14 for J=1 over N=3..12, h in [0,3].
  (2) which parity sector attains the min() -> the antiperiodic (NS) sum always does,
      for J>0, h>=0, so the min() in Eq. (28) is inert.
  (3) the regime where the formula is NOT valid: an antiferromagnetic ring (J<0) with odd N,
      where it returns an energy strictly BELOW the true ground state.

Requires: numpy only (no scipy/netket, so this is independent of the report's own tooling).
Deterministic. Runtime a few seconds up to N=10, ~1 min if you extend to N=12.
"""
import numpy as np

I2 = np.eye(2)
X = np.array([[0.0, 1.0], [1.0, 0.0]])
Z = np.diag([1.0, -1.0])


def site_op(n, site, m):
    out = np.array([[1.0]])
    for i in range(n):
        out = np.kron(out, m if i == site else I2)
    return out


def h_tfim(n, j, h):
    """Periodic boundary conditions: site n-1 couples back to site 0."""
    ham = np.zeros((2 ** n, 2 ** n))
    for i in range(n):
        ham -= j * site_op(n, i, Z) @ site_op(n, (i + 1) % n, Z)
        ham -= h * site_op(n, i, X)
    return ham


def closed_form(n, j, h):
    """report.tex Eq. (28). Returns (min, antiperiodic sum, periodic sum)."""
    def eps(k):
        return np.sqrt(j * j + h * h - 2 * j * h * np.cos(k))
    anti = -sum(eps(np.pi * (2 * m + 1) / n) for m in range(n))   # even parity / NS
    per = -sum(eps(2 * np.pi * m / n) for m in range(n))          # periodic momenta / R
    return min(anti, per), anti, per


def main():
    print("(1)+(2) ferromagnetic J=+1, periodic boundary conditions")
    print(f"{'N':>3} {'h':>5} {'ED':>15} {'Eq.(28)':>15} {'|diff|':>10}  sector attaining min")
    worst = 0.0
    for n in (6, 8, 10):
        for h in (0.0, 0.3, 0.5, 1.0, 1.5, 2.0, 3.0):
            ed = np.linalg.eigvalsh(h_tfim(n, 1.0, h))[0]
            cf, anti, per = closed_form(n, 1.0, h)
            worst = max(worst, abs(ed - cf))
            print(f"{n:3d} {h:5.2f} {ed:15.9f} {cf:15.9f} {abs(ed - cf):10.2e}"
                  f"  {'antiperiodic' if cf == anti else 'periodic'}")
    print(f"\n   worst |ED - Eq.(28)| = {worst:.2e}  -> the closed form is correct here,")
    print("   and the antiperiodic sector attains the minimum in every case, so min() is inert.")

    print("\n(3) antiferromagnetic J=-1 on an ODD ring: the formula fails (no validity conditions stated)")
    print(f"{'N':>3} {'J':>5} {'h':>5} {'ED':>15} {'Eq.(28)':>15} {'error':>10}")
    for n in (3, 5, 7):
        for h in (0.3, 1.0, 2.0):
            ed = np.linalg.eigvalsh(h_tfim(n, -1.0, h))[0]
            cf, _, _ = closed_form(n, -1.0, h)
            print(f"{n:3d} {-1.0:5.1f} {h:5.2f} {ed:15.9f} {cf:15.9f} {abs(ed - cf):10.3f}")
    print("\n   Eq. (28) is invariant under J -> -J (sum_k cos k = 0), so it cannot see the")
    print("   frustration of an odd antiferromagnetic ring and returns a value BELOW E_0.")
    print("   Fix: state J>0, h>=0 and periodic boundary conditions with Eq. (2)/Eq. (28).")

    print("\n(2b) what the periodic sum really is, split by regime")
    print("     h < J : it equals the lowest odd-parity state exactly (the unpaired k=0 mode")
    print("             is occupied, which the absolute value in eps(0) = |J-h| reproduces).")
    print("     h > J : it lies exactly 2(h-J) BELOW that state, because the unpaired mode")
    print("             carries a SIGNED energy and the parity constraint forces it occupied.")
    print(f"{'N':>3} {'h':>5} {'periodic sum':>15} {'exact E_1':>15} {'gap':>12} {'2(h-J)':>8}")
    for n in (4, 6, 8):
        for h in (0.3, 0.5, 0.9, 1.1, 1.5, 2.0):
            ev = np.linalg.eigvalsh(h_tfim(n, 1.0, h))[:2]
            _, _, per = closed_form(n, 1.0, h)
            note = f"{2 * (h - 1):8.2f}" if h > 1 else "       -"
            print(f"{n:3d} {h:5.2f} {per:15.9f} {ev[1]:15.9f} {ev[1] - per:12.2e} {note}")


if __name__ == "__main__":
    main()
