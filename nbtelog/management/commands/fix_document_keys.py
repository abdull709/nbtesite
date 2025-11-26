from django.core.management.base import BaseCommand
from django.db import transaction
from nbtelog.models import Document
from django.core.files.storage import default_storage
import urllib.parse


def generate_candidates(name):
    """Given a stored file name (possibly like 'documents/TEMPLATE_FOR_...pdf'),
    yield candidate object keys to try against storage.exists()."""
    if not name:
        return

    # Normalize separators
    name = name.lstrip('/')
    dirname, sep, fname = name.rpartition('/')

    fname_variants = set()
    fname_variants.add(fname)
    fname_variants.add(fname.replace('_', ' '))
    fname_variants.add(fname.replace(' ', '_'))
    # percent-encoded / decoded variants
    fname_variants.add(urllib.parse.unquote(fname))
    fname_variants.add(urllib.parse.quote(urllib.parse.unquote(fname), safe=''))

    dir_variants = set()
    if dirname:
        dir_variants.add(dirname)
        dir_variants.add(dirname.replace('documents', 'downloads'))
        dir_variants.add(dirname.replace('downloads', 'documents'))
    else:
        dir_variants.add('documents')
        dir_variants.add('downloads')

    candidates = []
    for d in dir_variants:
        for f in fname_variants:
            path = f"{d.rstrip('/')}/{f.lstrip('/')}"
            candidates.append(path)

    # Also try just the filename at top-level
    for f in fname_variants:
        candidates.append(f)

    # Keep order but remove duplicates
    seen = set()
    out = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


class Command(BaseCommand):
    help = 'Scan Document.file.name values, probe storage for likely object keys (underscore<->space, documents<->downloads) and optionally update DB to match the existing object key.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Only report changes, do not modify DB')
        parser.add_argument('--limit', type=int, default=0, help='Limit to N documents (0 = all)')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']

        qs = Document.objects.all().order_by('id')
        if limit and limit > 0:
            qs = qs[:limit]

        total = qs.count()
        self.stdout.write(f"Scanning {total} documents (dry_run={dry_run})...")

        storage = default_storage

        changed = 0
        not_found = 0
        for doc in qs:
            orig = doc.file.name or ''
            if not orig:
                self.stdout.write(f"[{doc.id}] no file.name stored, skipping")
                continue

            # If current name exists in storage, nothing to do
            try:
                if storage.exists(orig):
                    self.stdout.write(f"[{doc.id}] OK: {orig}")
                    continue
            except Exception as e:
                # Some storage backends may raise; continue to candidate probing
                self.stdout.write(f"[{doc.id}] storage.exists(orig) error: {e}")

            candidates = generate_candidates(orig)
            found = None
            for c in candidates:
                try:
                    if storage.exists(c):
                        found = c
                        break
                except Exception:
                    # Ignore storage probe errors for a candidate
                    continue

            if found:
                self.stdout.write(f"[{doc.id}] Found object for DB '{orig}' -> '{found}'")
                if not dry_run:
                    with transaction.atomic():
                        doc.file.name = found
                        doc.save(update_fields=['file'])
                    changed += 1
                else:
                    changed += 1
            else:
                self.stdout.write(f"[{doc.id}] No object found for '{orig}' (checked {len(candidates)} candidates)")
                not_found += 1

        self.stdout.write("--- Summary ---")
        self.stdout.write(f"Changed (or would change in dry-run): {changed}")
        self.stdout.write(f"Not found: {not_found}")
        self.stdout.write("Done.")
