package com.mycontacts.elastic.load;
import java.io.File;
import java.io.IOException;
import java.util.Scanner;
import com.mycontacts.elastic.model.Contacts;
import com.mycontacts.elastic.repository.ContactsRepository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.elasticsearch.core.ElasticsearchOperations;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.PostConstruct;
import java.util.ArrayList;
import java.util.List;

@Component
public class Loaders {

    @Autowired
    ElasticsearchOperations operations;

    @Autowired
    ContactsRepository contactsRepository;

    @PostConstruct
    @Transactional
    public void loadAll(){

        operations.putMapping(Contacts.class);
        System.out.println("Loading Data");
        contactsRepository.save(getData());
        System.out.printf("Loading Completed");

    }

    private List<Contacts> getData() {
    	
        List<Contacts> contactses = new ArrayList<>();
        Loaders obj = new Loaders();
        
        contactses = obj.getFile("file/contactsData.txt");
        
        System.out.println(contactses.size());
        return contactses;
    }
    
    private List<Contacts> getFile(String fileName) {
    	List<Contacts> contactsesfromfile = new ArrayList<>();
    	StringBuilder result = new StringBuilder("");

    	//Get file from resources folder
    	ClassLoader classLoader = getClass().getClassLoader();
    	File file = new File(classLoader.getResource(fileName).getFile());
    	long intCounter;
    	intCounter = 0;
    	try (Scanner scanner = new Scanner(file)) {

    		while (scanner.hasNextLine()) {
    			String line = scanner.nextLine();
    			String[] parts = line.split(",");
    			System.out.println(line);
    			intCounter +=1;
    			contactsesfromfile.add(new Contacts(parts[0],parts[2],parts[1],parts[3], intCounter, "", 0L));
    			result.append(line).append("\n");
    		}

    		scanner.close();

    	} catch (IOException e) {
    		e.printStackTrace();
    	}

    	return contactsesfromfile;

      }
}
