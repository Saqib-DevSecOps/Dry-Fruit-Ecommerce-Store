from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def relative_url(value, field_name, urlencode=None):
    url = '?{}={}'.format(field_name, value)
    if urlencode:
        querystring = urlencode.split('&')
        filtered_querystring = filter(lambda p: p.split('=')[0] != field_name, querystring)
        encoded_querystring = '&'.join(filtered_querystring)
        url = '{}&{}'.format(url, encoded_querystring)
    return url


@register.filter
def get_html_icons(value):
    value = str(value)
    if value == '5':
        return mark_safe(
            '<li class="active"><i class="fas fa-star"></i></li>'
            '<li class="active"><i class="fas fa-star"></i></li>'
            '<li class="active"><i class="fas fa-star"></i></li>'
            '<li class="active"><i class="fas fa-star"></i></li>'
            '<li class="active"><i class="fas fa-star"></i></li>'
        )
    elif value == '4':
        return mark_safe(
            '<li class="active"><i class="fas fa-star"></i></li>'
            '<li class="active"><i class="fas fa-star"></i></li>'
            '<li class="active"><i class="fas fa-star"></i></li>'
            '<li class="active"><i class="fas fa-star"></i></li>'
            '<li><i class="fas fa-star"></i></li>'
        )
    elif value == '3':
        return mark_safe(
            '<li class="active"><i class="fas fa-star"></i></li>'
            '<li class="active"><i class="fas fa-star"></i></li>'
            '<li class="active"><i class="fas fa-star"></i></li>'
            '<li><i class="fas fa-star"></i></li>'
            '<li><i class="fas fa-star"></i></li>'
        )
    elif value == '2':
        return mark_safe(
            '<li class="active"><i class="fas fa-star"></i></li>'
            '<li class="active"><i class="fas fa-star"></i></li>'
            '<li><i class="fas fa-star"></i></li>'
            '<li><i class="fas fa-star"></i></li>'
            '<li><i class="fas fa-star"></i></li>'
        )
    elif value == '1':
        return mark_safe(
            '<li class="active"><i class="fas fa-star"></i></li>'
            '<li><i class="fas fa-star"></i></li>'
            '<li><i class="fas fa-star"></i></li>'
            '<li><i class="fas fa-star"></i></li>'
            '<li><i class="fas fa-star"></i></li>'
        )
    elif value == '0':
        return mark_safe(
            '<li><i class="fas fa-star"></i></li>'
            '<li><i class="fas fa-star"></i></li>'
            '<li><i class="fas fa-star"></i></li>'
            '<li><i class="fas fa-star"></i></li>'
            '<li><i class="fas fa-star"></i></li>'
        )



@register.filter
def get_html_icons_for_filter(value):
    value = str(value)
    if value == '5':
        return mark_safe('<i class="fas fa-star text-warning"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star text-warning"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star text-warning"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star text-warning"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star text-warning"></i>')
    elif value == '4':
        return mark_safe('<i class="fas fa-star  text-warning"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star  text-warning"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star text-warning"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star text-warning"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star"></i>')
    elif value == '3':
        return mark_safe('<i class="fas fa-star  text-warning"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star  text-warning"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star text-warning"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star"></i>')
    elif value == '2':
        return mark_safe('<i class="fas fa-star  text-warning"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star  text-warning"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star"></i>')
    elif value == '1':
        return mark_safe('<i class="fas fa-star  text-warning"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star"></i>')
    elif value == '0':
        return mark_safe('<i class="fas fa-star"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star"></i>&nbsp;&nbsp;'
                         '<i class="fas fa-star"></i>')

@register.filter
def image_or_placeholder(image, placeholder=None):
    if image:
        if hasattr(image, 'url') and image.url:
            return image.url
        else:
            return image
    if placeholder:
        return f"https://placehold.co/{placeholder}"
    return "https://placehold.co/100"


@register.filter
def multiply(value, arg):
    return value * arg


@register.filter
def alert_type_class(value):
    if value in ['cod', 'delivery', 'in_transit', 'bank_account', 'applied','online']:
        return 'primary'
    elif value in ['completed', 'success', 'paid', 'card', 'approved']:
        return 'success'
    elif value in ['pending', 'draft']:
        return 'warning'
    elif value in ['cancel', 'cancelled', 'unpaid', 'failed', 'banned']:
        return 'danger'
    else:
        return 'secondary'


