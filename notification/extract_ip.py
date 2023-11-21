def get_user_ip(request):
    """
    Get the user's IP address from the Django request object.

    Args:
        request (HttpRequest): The Django request object.

    Returns:
        str: The IP address of the user.
    """

    # The 'HTTP_X_FORWARDED_FOR' header will be set if the user is behind a proxy or load balancer.
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    print(x_forwarded_for)
    if x_forwarded_for:
        # The real IP address might be the first one in the list
        ip = x_forwarded_for.split(',')[0]
    else:
        # If there is no 'HTTP_X_FORWARDED_FOR' header, use 'REMOTE_ADDR'
        ip = request.META.get('REMOTE_ADDR')

    return ip
