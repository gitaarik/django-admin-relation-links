from setuptools import setup


with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='django-admin-relation-links',
    keywords='django admin relation foreignkey link',
    version='0.2.3',
    author='gitaarik',
    author_email='gitaarik@posteo.net',
    packages=['django_admin_relation_links'],
    url='https://github.com/gitaarik/django-admin-relation-links/',
    license='GNU Lesser General Public License v3 (LGPLv3)',
    description='An easy way to add links to relations in the Django Admin site.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3'
)
