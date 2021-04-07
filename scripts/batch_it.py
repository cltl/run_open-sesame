from glob import glob
from shutil import rmtree, copy
import os

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield i, i+n, lst[i:i + n]

batch_size = 5000
absolute_dir_path = '/home/postma/GVA/output/Q5618454/wiki_output/en'
batches_dir = 'naf_batches'

naf_paths = glob(f'{absolute_dir_path}/*naf')

print(f'found {len(naf_paths)} naf paden')

if os.path.exists(batches_dir):
    rmtree(batches_dir)
    print(f'removed {batches_dir}')

os.mkdir(batches_dir)
print(f'created {batches_dir}')

for batch_start, batch_end, batch in chunks(lst=naf_paths,
                                            n=batch_size):

    batch_dir = os.path.join(batches_dir, f'{batch_start}---{batch_end}')
    os.mkdir(batch_dir)
    print(f'created {batch_dir}')

    for naf_path in batch:
        copy(naf_path, batch_dir)


