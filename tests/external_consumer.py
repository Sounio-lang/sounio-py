import asyncio
import json
import os
from pathlib import Path
import tempfile
import sounio

results=[]
assert 'site-packages' in sounio.__file__, sounio.__file__
source='fn main() -> i32 { 23 }'
with tempfile.TemporaryDirectory(prefix='python consumer ') as directory:
    os.chdir(directory)
    path=Path('input.sio'); path.write_text(source)
    executor=sounio.SounioExecutor()
    assert executor.check_file(str(path)).success
    results.append('check')
    assert executor.run_file(str(path)).exit_code==23
    results.append('run_file')
    assert executor.run_code(source).exit_code==23
    results.append('run_code')
    assert asyncio.run(executor.async_run_code(source)).exit_code==23
    results.append('async_run_code')
    with sounio.compile_sio(source) as module:
        assert module.run().exit_code==23
    results.append('compile_sio')
    assert sounio.run_sio(source).exit_code==23
    results.append('run_sio')
    stdlib='use cmp::lib::max_i64\nfn main() -> i32 { if max_i64(2, 3) == 3 { 0 } else { 1 } }'
    result=executor.run_code(stdlib)
    assert result.exit_code==0, (result.stderr,result.stdout,result.exit_code)
    results.append('bundled_stdlib')
    invalid=Path('invalid.sio'); invalid.write_text('fn main() -> i32 { missing_name }')
    assert not executor.check_file(str(invalid)).success
    try:
        sounio.compile_sio(invalid)
    except RuntimeError:
        results.append('invalid_compile_refused')
    else:
        raise AssertionError('invalid compilation accepted')
print(json.dumps({'status':'PASS','package':sounio.__file__,'checks':results},indent=2))
