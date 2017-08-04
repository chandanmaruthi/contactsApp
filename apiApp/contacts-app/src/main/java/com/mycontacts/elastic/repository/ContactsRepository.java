package com.mycontacts.elastic.repository;


import com.mycontacts.elastic.model.Contacts;
import org.springframework.data.elasticsearch.repository.ElasticsearchRepository;

import java.util.List;

public interface ContactsRepository extends ElasticsearchRepository<Contacts, Long> {
    List<Contacts> findByName(String text);

    List<Contacts> findBySalary(Long salary);
}
