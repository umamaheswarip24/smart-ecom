package com.example.inventory;
import java.util.Map;
import java.util.List;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestBody;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.PathVariable;

@RestController
@RequestMapping("/inventory")
public class InventoryController {

    private final StockRepository repo;

    public InventoryController(StockRepository repo) {
        this.repo = repo;
    }

    @PostMapping("/update")
    public List<Stock> update(@RequestBody Map<String, Integer> items) {
        items.forEach((name, qty) -> {
            Stock s = new Stock();
            s.setName(name);
            s.setQty(qty);
            repo.save(s);
        });
        return repo.findAll();
    }

    @GetMapping("/view")
    public List<Stock> view() {
        return repo.findAll();
    }

    // POST - Insert new inventory item
@PostMapping("/add")
public Stock add(@RequestBody Stock item) {
    return repo.save(item);
}

// GET - Retrieve a specific item by ID
@GetMapping("/{id}")
public Stock getById(@PathVariable Integer id) {
    return repo.findById(id).orElseThrow();
}

// PUT - Update quantity after purchase
@PutMapping("/update/{id}")
public Stock updateQty(@PathVariable Integer id, @RequestBody Map<String, Integer> body) {
    Stock s = repo.findById(id).orElseThrow();
    s.setQty(body.get("qty"));
    return repo.save(s);
}

}