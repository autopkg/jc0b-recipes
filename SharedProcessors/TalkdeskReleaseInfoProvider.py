#!/usr/local/autopkg/python

import requests

from autopkglib import APLooseVersion, Processor, ProcessorError

__all__ = ["TalkdeskReleaseInfoProvider"]

TALKDESK_BUCKET="https://td-infra-prd-us-east-1-s3-atlaselectron.s3.amazonaws.com"

class TalkdeskReleaseInfoProvider(Processor):
    description = (
        "Gets the download URL and version for the latest version of Talkdesk from their installer bucket."
    )
    output_variables = {
        "url": {
            "description": (
                "The URL for the latest release."
            )
        },
        "version": {
            "description": (
                "Version info for the latest release."
            )
        }
    }

    __doc__ = description

    def get_latest(self):
        releases = requests.get(f"{TALKDESK_BUCKET}/talkdesk-latest-metadata.json", allow_redirects=True)
        if releases.status_code != 200:
            raise ProcessorError(f"Unexpected status code {releases.status_code} while trying to get releases.")
        # Convert bytes to string
        release_versions = releases.json()

        for version in release_versions:
            for target in version["targets"]:
                if target["os"] == "Mac":
                    self.output(f'Found version {version["version"]}!')
                    return version["version"]

        raise ProcessorError(f"No macOS version of Talkdesk was found in {TALKDESK_BUCKET}/talkdesk-latest-metadata.json.")

    def main(self):
        # Get our list of releases
        latest_version = self.get_latest()

        self.env["version"] = latest_version
        self.env["url"] = f"{TALKDESK_BUCKET}/talkdesk-{latest_version}.dmg"


if __name__ == "__main__":
    PROCESSOR = TalkdeskReleaseInfoProvider()
    PROCESSOR.execute_shell()