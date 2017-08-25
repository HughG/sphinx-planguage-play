Chapter 1
***********

..  _some-requirements:

Some Requirements
=====================

:Tag: FR:Foo.Bar.baz
:Source: :ref:`hughg`
:Gist: Bar the baz
:Description: The user should be able to prevent access by any baz.


JS Stuff
=========

..  js:module:: Foo

..  js:class:: MyAnimal(name[, age])

    :param string name: The name of the animal
    :param number age: an optional age for the animal

..  js:function:: $.getJSON(href, callback[, errback])

    :param string href: An URI to the location of the resource.
    :param callback: Gets called with the object.
    :param errback:
        Gets called in case the request fails. And a lot of other
        text so we need multiple lines.
    :throws SomeError: For whatever reason in that case.
    :returns: Something.

    See also :js:meth:`getJSON`, :js:meth:`MyAnimal.getJSON`, :js:meth:`MyAnimal.thisMethodHasAVeryLongName`.

..  js:method:: MyAnimal.getJSON(href, callback[, errback])

    :param string href: An URI to the location of the resource.
    :param callback: Gets called with the object.
    :param errback: Gets called in case the request fails. And a lot of other
        text so we need multiple lines.
    :throws SomeError: For whatever reason in that case.
    :returns: Something.

..  js:method:: MyAnimal.thisMethodHasAVeryLongName(href, callback[, errback])

    :param string href: An URI to the location of the resource.
    :param callback: Gets called with the object.
    :param errback: Gets called in case the request fails. And a lot of other
        text so we need multiple lines.
    :throws SomeError: For whatever reason in that case.
    :returns: Something.
