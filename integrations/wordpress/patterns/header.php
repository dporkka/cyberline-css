<?php
/**
 * Title: Syntyr site header
 * Slug: syntyr/header
 * Categories: header
 * Description: Editable brand, navigation links and call-to-action.
 */
?>
<!-- wp:group {"tagName":"header","className":"syn-root syn-header","layout":{"type":"flex","flexWrap":"wrap","justifyContent":"space-between"}} -->
<header class="wp-block-group syn-root syn-header">
  <!-- wp:site-title {"level":0,"className":"syn-heading"} -->
  <p class="wp-block-site-title syn-heading"><a href="/">Site name</a></p>
  <!-- /wp:site-title -->
  <!-- wp:group {"tagName":"nav","className":"syn-nav","layout":{"type":"flex","flexWrap":"wrap"}} -->
  <nav class="wp-block-group syn-nav">
    <!-- wp:paragraph --><p><a href="/services">Services</a></p><!-- /wp:paragraph -->
    <!-- wp:paragraph --><p><a href="/work">Work</a></p><!-- /wp:paragraph -->
    <!-- wp:paragraph --><p><a href="/journal">Journal</a></p><!-- /wp:paragraph -->
  </nav>
  <!-- /wp:group -->
  <!-- wp:buttons -->
  <div class="wp-block-buttons">
    <!-- wp:button {"className":"syn-button syn-button--primary"} -->
    <div class="wp-block-button syn-button syn-button--primary"><a class="wp-block-button__link wp-element-button" href="/contact">Contact us</a></div>
    <!-- /wp:button -->
  </div>
  <!-- /wp:buttons -->
</header>
<!-- /wp:group -->
