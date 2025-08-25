To use this module, you need to install Advanced Custom Fields (https://www.advancedcustomfields.com/) plugin on WooCommerce WPML:

* Go to ACF menu
* Create a new field group (+ Add New)
* Create the follow fields:
    * "additional_information" as editor field in product.
    * "video_gallery" as repeater field in product with subfields:
        * "video" as oEmbed field
        * "video_description" as text field
* In the same page, in settings, create the rule:
   * Post type is equal to Product

* This module uses the ACF WooCommerce plugin to update the value of ACF custom fields in WooCommerce products through the REST API.
* The WordPress plugin must be installed and can be found at https://github.com/nuobit/acf-woocommerce.
