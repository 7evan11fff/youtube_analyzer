#!/usr/bin/env python3
"""
License key generator for YouTube Niche Analyzer.
Run this to create valid keys — keep the output private.

Usage:
    python keygen.py --tier pro --count 5
    python keygen.py --tier free --count 10
"""

import argparse
from licensing import generate_key, TIER_FREE, TIER_PRO


def main():
    parser = argparse.ArgumentParser(description="Generate YouTube Niche Analyzer license keys")
    parser.add_argument("--tier", choices=["free", "pro"], required=True,
                        help="Key tier: 'free' or 'pro'")
    parser.add_argument("--count", type=int, default=1,
                        help="Number of keys to generate (default: 1)")
    args = parser.parse_args()

    print(f"\nGenerating {args.count} {args.tier.upper()} key(s):\n")
    for i in range(args.count):
        key = generate_key(args.tier)
        print(f"  {key}")
    print()


if __name__ == "__main__":
    main()
