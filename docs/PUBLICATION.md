# Public source boundary

Public source contains original requirements, composition metadata, contribution
guidance and CI. Private conversations, installation inventories, machine/account
identifiers, authentication, screenshots, disk images and private Git histories
belong outside the source export. Keep product requirements when removing private
operational notes. Do not confuse publication with an implemented OS release.

## Before changing visibility

1. Review the exact exported files and all branch/tag history, including author
   and committer metadata. Use no-reply project identities and preserve legitimate
   third-party attribution. Ignore rules do not remove tracked files or history.
2. Check licenses, documentation links and the public Lina revision. Run the
   [CI commands](CI.md) and inspect their actual coverage and limits.
3. Configure and read back the branch protections in [POLICY](../POLICY.md).
   Confirm both successful and failed checks affect the intended PR gate.
4. After the final hosted merge, freeze the actual remote refs and inspect source,
   metadata, PR bodies/comments/reviews, issues, Actions logs/summaries/artifacts
   and releases. A changed ref or failed check requires a fresh inspection before
   visibility changes. Store detailed private findings outside public source.
5. Obtain owner authorization for publication, apply visibility, and re-read
   repository rules, anonymous source access and private vulnerability reporting.

If replacing a repository, preserve the original separately and change every
preserved checkout's fetch/push origin before reusing the old repository name.
Verify the archive's repository identity and private state. Never push the old
root or an archive branch into the replacement public repository.

GitHub makes Actions history and logs visible with a public repository. History
rewriting or later visibility changes do not erase third-party copies. See
[GitHub visibility documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility).

## Evidence and limits

Keep exact source/ref identifiers, commands and outcomes, relevant hosted run/PR
links and settings readback. Secret and privacy scans are aids to source review,
not proof that every possible sensitive value has been detected. Public source
must remain free of detailed private findings and archive inventories.

Source publication does not publish an OS image, create a package release,
install software or update user data. Those actions follow [ACCEPTANCE](ACCEPTANCE.md)
and their separate authorization.
