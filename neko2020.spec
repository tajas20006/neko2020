# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

projpath = os.path.dirname(os.path.abspath(SPEC))

a = Analysis([os.path.join(projpath, 'neko2020', '__main__.py')],
             pathex=[projpath],
             binaries=[],
             datas=[('config/default_config.yml', 'config')],
             hiddenimports=['pkg_resources'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          Tree('resource', prefix='resource'),
          [],
          name='neko2020',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='resource/neko/Awake.ico')
