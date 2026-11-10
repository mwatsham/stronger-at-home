#!/usr/bin/env python3
"""Isolated loopback preview; no connection to either hosted website."""
import argparse
import getpass
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import tempfile

if __package__:
    from .staging_design_preview import include_staging_preview
else:
    from staging_design_preview import include_staging_preview


def prepare_preview(root: Path, workspace: Path, port: int, password: str):
    root=root.resolve()
    workspace=workspace.resolve()
    public=workspace/'public'
    private=workspace/'private'
    if public.is_symlink() or private.is_symlink():
        raise ValueError('Preview directories must not be symlinks')
    private.mkdir(mode=0o700,exist_ok=True)
    config=private/'feedback.php'
    if not config.exists():
        result=subprocess.run(['php',str(root/'scripts/setup_feedback.php'),'--directory='+str(private),'--environment=local','--origin=http://127.0.0.1:'+str(port),'--password-stdin'],input=password.encode(),capture_output=True)
        if result.returncode:
            raise RuntimeError('Private local setup failed: '+result.stderr.decode())
        quotes=[
            {'text':'Preview sample: patient feedback will appear here once Melanie has approved it for publication.','attribution':'Demonstration only — not a patient review'},
            {'text':'Preview sample: use Next and Previous to browse quotes, or Pause to read at your own pace.','attribution':'Demonstration only — not a patient review'},
            {'text':'Preview sample: Melanie can add, edit and publish agreed quotes from her private feedback manager.','attribution':'Demonstration only — not a patient review'},
        ]
        records=[dict(q,id=secrets.token_hex(16),order=i,status='published',consent=True) for i,q in enumerate(quotes)]
        (private/'quotes.json').write_text(json.dumps({'revision':0,'records':records}))
        (private/'quotes.json').chmod(0o600)
    # Rebuild the public copy only. The runtime store deliberately stays outside it.
    shutil.copytree(root/'site',public,dirs_exist_ok=True)
    (workspace/'release.json').write_text('{"publicationMode":"enquiries"}')
    # The approved photo helper requires new asset destinations.
    for name in ('assets/approved-photos','design-preview'):
        dest=public/name
        if dest.exists():
            if dest.is_symlink(): raise ValueError('Unsafe preview asset destination')
            shutil.rmtree(dest)
    include_staging_preview(root,public,'production',approved_production=True)
    home=public/'index.html'
    home.write_text(home.read_text().replace('<body>','<body><p class="notice">Local preview — demonstration quotes only. No live website is connected. <a href="/feedback/admin/">Open feedback manager</a></p>',1))
    router=workspace/'router.php'
    router.write_text('<?php if (str_starts_with(parse_url($_SERVER["REQUEST_URI"], PHP_URL_PATH), "/api/")) { http_response_code(503); echo "Enquiries disabled in local preview."; return true; } return false;')
    return public,config


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port',type=int,default=58640)
    p.add_argument('--password-file',type=Path)
    p.add_argument('--generate-local-password',action='store_true')
    args=p.parse_args()
    if not 1024<=args.port<=65535: p.error('Choose a port from 1024 to 65535.')
    workspace=Path(tempfile.mkdtemp(prefix='sah-feedback-preview-')).resolve()
    workspace.chmod(0o700)
    if args.password_file:
        if args.password_file.stat().st_mode&0o077: p.error('Password file must be owner-only.')
        password=args.password_file.read_text().rstrip('\r\n')
    elif args.generate_local_password:
        password=secrets.token_urlsafe(24)
        credential=workspace/'local-preview-password.txt'
        descriptor=os.open(credential,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(descriptor,'w') as f: f.write(password)
        print('Local-only password file: '+str(credential),flush=True)
    else:
        password=getpass.getpass('Choose a local preview password (16–72 bytes): ')
    public,config=prepare_preview(Path(__file__).resolve().parents[1],workspace,args.port,password)
    password=''
    print('Local preview: http://127.0.0.1:'+str(args.port)+'/#share-your-experience',flush=True)
    print('Feedback manager: http://127.0.0.1:'+str(args.port)+'/feedback/admin/',flush=True)
    print('Private preview workspace: '+str(workspace),flush=True)
    env=dict(os.environ,STRONGER_HOME_FEEDBACK_CONFIG=str(config))
    try:
        subprocess.run(['php','-S','127.0.0.1:'+str(args.port),'-t',str(public),str(workspace/'router.php')],env=env,check=True)
    except KeyboardInterrupt:
        pass

if __name__=='__main__':
    main()
