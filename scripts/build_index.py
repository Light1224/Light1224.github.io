import argparse

from site_builder_core import build_all, scaffold_project, scaffold_project_post, validate_content


def parse_args():
    parser = argparse.ArgumentParser(description="Build and manage site content.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("build", help="Build all site pages (default)")
    subparsers.add_parser("check", help="Validate content metadata")

    new_parser = subparsers.add_parser("new", help="Create a new project")
    new_parser.add_argument("--section", choices=["projects"], required=True)
    new_parser.add_argument("--slug", required=True, help="Project slug / folder name")
    new_parser.add_argument("--title", required=True, help="Project title")

    post_parser = subparsers.add_parser("new-post", help="Create a new post/page inside an existing project")
    post_parser.add_argument("--project", required=True, help="Existing project slug")
    post_parser.add_argument("--slug", required=True, help="Post slug / file name")
    post_parser.add_argument("--title", required=True, help="Post title")

    return parser.parse_args()


def main():
    args = parse_args()
    command = args.command or "build"

    if command == "build":
        build_all()
        print("Site rebuilt successfully.")
        return

    if command == "check":
        ok = validate_content()
        raise SystemExit(0 if ok else 1)

    if command == "new":
        created_path = scaffold_project(args.slug, args.title)
        print(f"Created: {created_path}")
        print("Now run: python3 scripts/build_index.py")
        return

    if command == "new-post":
        created_path = scaffold_project_post(args.project, args.slug, args.title)
        print(f"Created: {created_path}")
        print("Now run: python3 scripts/build_index.py")
        return

    raise SystemExit(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
