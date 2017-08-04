package com.mycontacts.elastic.resource;


import com.mycontacts.elastic.model.Contacts;
import com.mycontacts.elastic.repository.ContactsRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/rest/search")
public class SearchResource {

    @Autowired
    ContactsRepository contactsRepository;

    @GetMapping(value = "/name/{text}")
    public List<Contacts> searchName(@PathVariable final String text) {
        return contactsRepository.findByName(text);
       
    }


    @GetMapping(value = "/salary/{salary}")
    public List<Contacts> searchSalary(@PathVariable final Long salary) {
        return contactsRepository.findBySalary(salary);
    }


    @GetMapping(value = "/all")
    public List<Contacts> searchAll() {
        List<Contacts> contactsList = new ArrayList<>();
        Iterable<Contacts> contactses = contactsRepository.findAll();
        contactses.forEach(contactsList::add);
        return contactsList;
    }


}

