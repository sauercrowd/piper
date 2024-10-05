import argparse
from .installer import piper_install

def main():
    parser = argparse.ArgumentParser(description="Piper: Custom Package Installer")
    parser.add_argument("package_spec", help="Package specification (e.g., package==version)")
    parser.add_argument("suffix", help="Suffix for renaming the package")

    args = parser.parse_args()

    piper_install(args.package_spec, args.suffix)

if __name__ == "__main__":
    main()
