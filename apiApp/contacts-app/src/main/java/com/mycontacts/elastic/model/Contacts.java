package com.mycontacts.elastic.model;

import org.springframework.data.elasticsearch.annotations.Document;

@Document(indexName = "contacts", type = "contacts", shards = 1)
public class Contacts {

    private String name;
    private String phone;
    private String email;
    private String address;

    private Long id;
    private String teamName;
    private Long salary;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getAdress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    
    
    
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTeamName() {
        return teamName;
    }

    public void setTeamName(String teamName) {
        this.teamName = teamName;
    }

    public Long getSalary() {
        return salary;
    }

    public void setSalary(Long salary) {
        this.salary = salary;
    }

    public Contacts(String name,String phone,String email,String address, Long id, String teamName, Long salary) {

        this.name = name;
        this.phone = phone;
        this.email = email;
        this.address = address;
        this.id = id;
        this.teamName = teamName;
        this.salary = salary;
    }

    public Contacts() {

    }
}
