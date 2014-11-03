.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Thu Dec  6 12:28:25 CET 2012

==============
 User's Guide
==============

This package contains the access API and descriptions for the `AR face`_ database.
It only contains the Bob_ accessor methods to use the DB directly from python, with our certified protocols.
The actual raw data for the database should be downloaded from the original URL (though we were not able to contact the corresponding Professor).

Our version of the `AR face`_ database contains 3312 images from 136 persons, 76 men and 60 women.
We split the database into several protocols that we have designed ourselves.
The identities are split up into three groups:

* the 'world' group for training your algorithm
* the 'dev' group to optimize your algorithm parameters on
* the 'eval' group that should only be used to report results

Additionally, there are different protocols:

* ``'expression'``: only the probe files with different facial expressions are selected
* ``'illumination'``: only the probe files with different illuminations are selected
* ``'occlusion'``: only the probe files with normal illumination and different accessories (scarf, sunglasses) are selected
* ``'occlusion_and_illumination'``: only the probe files with strong illumination and different accessories (scarf, sunglasses) are selected
* ``'all'``: all files are used as probe

In any case, the images with neutral facial expression, neutral illumination and without accessories are used for enrollment.



The Database Interface
----------------------

The :py:class:`bob.db.arface.Database` complies with the standard biometric verification database as described in :ref:`commons`, implementing the interface :py:class:`bob.db.verification.utils.SQLiteDatabase`.

.. todo::
   Explain the particularities of the :py:class:`bob.db.arface.Database`.


.. _ar face: http://www2.ece.ohio-state.edu/~aleix/ARdatabase.html
.. _bob: https://www.idiap.ch/software/bob
