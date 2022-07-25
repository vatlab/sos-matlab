import subprocess


def test_script_to_notebook(sample_m_script):
    '''Test sos show script --notebook'''
    assert 0 == subprocess.call(
        f'sos convert {sample_m_script} {sample_m_script[:-2]}.ipynb',
        shell=True)
    assert 0 == subprocess.call(
        f'sos convert {sample_m_script} {sample_m_script[:-2]}.ipynb --use-sos',
        shell=True)
    assert 0 == subprocess.call(
        f'sos convert {sample_m_script} {sample_m_script[:-2]}.ipynb --use-sos --kernel=matlab',
        shell=True)
