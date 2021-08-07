$(document).ready(function () {
  const sections = $('div.section');
  let activeLink = null;
  const bottomHeightThreshold = $(document).height() - 30;

  $(window).scroll(function (event) {
    const distanceFromTop = $(this).scrollTop();
    let currentSection = null;

    if(distanceFromTop + window.innerHeight > bottomHeightThreshold) {
      currentSection = $(sections[sections.length - 1]);
    }
    else {
      sections.each(function () {
        const section = $(this);
        if (section.offset().top - 1 < distanceFromTop) {
          currentSection = section;
        }
      });
    }

    if (activeLink) {
      activeLink.parent().removeClass('active');
    }

    if (currentSection) {
      activeLink = $('.sphinxsidebar a[href="#' + currentSection.attr('id') + '"]');
      activeLink.parent().addClass('active');
    }
  });
});