openerp.mozaik_base = function(instance) {
    instance.web.search.ManyToOneField
                                      .include({
        make_domain: function (name, operator, facetValue) {
           var self = this,
               operator = facetValue.get('operator') || operator;

        switch(operator){
          case 'not child_of':
              return ['!',[name, 'child_of', facetValue.get('value')]];
        }
        return self._super(name, operator, facetValue);
    },
    });
};
