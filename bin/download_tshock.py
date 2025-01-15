#!/usr/bin/env python3

import os
import sys
import json
import platform
from http.client import HTTPSConnection, HTTPResponse
from urllib.parse import urlparse

GITHUB_API = "api.github.com"
REPO_API_PATH = "/repos/Pryaxis/TShock"
LATEST_PATH = f"{REPO_API_PATH}/releases/latest"
RELEASE_TAG_PATH = f"{REPO_API_PATH}/releases/tags"
ASSET_URI = f"{REPO_API_PATH}/releases/assets"

ARCH_MAP = {
    "aarch64": "arm64",
    "x86_64": "amd64",
}


def get_https_response(host, path, headers: dict = None):
    if headers is None:
        headers = {}
    cx = HTTPSConnection(host)
    cx.request("GET", path, headers={"User-Agent": "python", **headers})
    return cx.getresponse()


def get_github_api_response(path, headers: dict = None):
    return get_https_response(GITHUB_API, path, headers)


def get_github_api_payload(path):
    return json.load(get_github_api_response(path))


def get_latest_release():
    return get_github_api_payload(LATEST_PATH)


def get_tag_release(tag: str):
    return get_github_api_payload(f"{RELEASE_TAG_PATH}/{tag}")


def get_release():
    release = os.environ.get("RELEASE_TAG", None)

    if release is None:
        return get_latest_release()
    return get_tag_release(release)


def get_asset_suffix():
    plat = platform.machine()
    arch = ARCH_MAP.get(plat, plat)
    return f"linux-{arch}-Release.zip"


def download_asset(response: HTTPResponse):
    with open("./tshock.zip", "wb") as fd:
        fd.write(response.read())


def get_asset(asset_id: int):
    resp = get_github_api_response(f"{ASSET_URI}/{asset_id}", {
        "Accept": "application/octet-stream",
    })

    if resp.status == 200:
        download_asset(resp)
    else:
        url = urlparse(resp.headers.get("location"))
        resp = get_https_response(url.hostname, f"{url.path}?{url.query}")
        download_asset(resp)


def get_asset_id(release: dict):
    suffix = get_asset_suffix()
    assets: list[dict[str, str | int]] = release["assets"]

    for asset in assets:
        if asset["name"].endswith(suffix):
            return int(asset["id"])

    print(f"asset not found ending with {suffix}")
    sys.exit(1)


def main():
    release = get_release()
    asset_id = get_asset_id(release)
    get_asset(asset_id)


if __name__ == "__main__":
    main()
