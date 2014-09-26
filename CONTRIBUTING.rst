어떻게 참여하는지에 대하여
=================

commit hook 설정하는 법
------------------------

.. code-block:: console

   $ mkdir -p .git/hooks/
   $ ln -s `pwd`/hooks/pre-commit .git/hooks/


다운로드 종속성 설치법
----------------------------

.. code-block:: console

   $ pip install -e .


The Perils of Rebasing
----------------------

Do not rebase commits that you have pushed to a public repository.

Refer http://git-scm.com/book/en/Git-Branching-Rebasing#The-Perils-of-Rebasing

Use

.. code-block:: console

   $ git pull --rebase
