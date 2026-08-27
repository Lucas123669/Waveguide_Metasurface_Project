import os


def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_workspace_path(*parts):
    root = os.environ.get("GWM_WORKFLOW_WORKSPACES_DIR")
    if root:
        if not os.path.isabs(root):
            root = os.path.join(get_project_root(), root)
    else:
        root = os.path.join(get_project_root(), "workspaces")
    return os.path.abspath(os.path.join(root, *parts))
